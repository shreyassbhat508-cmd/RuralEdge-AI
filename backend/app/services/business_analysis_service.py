"""Business Analysis Service for POST /api/business/analyze.

Orchestrates existing services without duplicating any business logic:
  - finance/ engine  : loan EMI, interest, profitability calculations
  - recommendation_service : deterministic scheme matching
  - All market/competitor data is pending for phase 1

Design principles:
  1. Never invent financial data — use the finance/ calculator with real inputs.
  2. When operational revenue/cost data is not in the request (phase 1), the
     finance section returns the structural facts (project cost, loan amount,
     EMI at default rate) clearly labelled as estimates.
  3. Market section is explicitly labelled 'pending' — no fake numbers.
  4. SWOT is derived deterministically from the inputs; no AI hallucination.
"""

import logging
from typing import Any, Dict, List, Optional

from app.schemas.business import (
    BusinessAnalyzeRequest,
    BusinessAnalyzeResponse,
    BusinessInfo,
    FinanceInfo,
    MarketInfo,
    OpportunityInfo,
    SchemeInfo,
    SwotAnalysis,
)
from app.schemas.recommendation import RecommendationRequest
from app.services.recommendation_service import get_recommendations

# Finance engine imports – reuse the existing calculator, not the simpler
# loan_calculator_service, because we need EMI with the reducing-balance formula.
from finance.calculator import _calculate_loan_emi  # type: ignore[attr-defined]
from app.services.feasibility_scoring_service import calculate_feasibility_score
from app.services.google_places_service import get_google_places_competitor_analysis

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Default loan parameters used when no scheme data is available yet.
# These are industry-standard indicative values clearly surfaced as estimates.
_DEFAULT_INTEREST_RATE: float = 7.0          # 7 % p.a. (Mudra/NABARD ballpark)
_DEFAULT_REPAYMENT_MONTHS: int = 60          # 5 years

_OPPORTUNITY_THRESHOLDS = [
    (75, "High"),
    (50, "Medium"),
    (25, "Low"),
    (0, "Very Low"),
]

_CALCULATION_NOTE = (
    "Estimated calculation for planning purposes. Actual loan terms, interest "
    "calculation, EMI, subsidy, moratorium and repayment schedule depend on the "
    "applicable government scheme and lending institution."
)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _build_finance_section(
    project_cost: float,
    margin_capital: float,
) -> FinanceInfo:
    """Compute loan structural data using the finance/ engine's EMI calculator.

    Monthly revenue and operating cost are not part of the phase-1 request, so
    those fields remain 0 and the caller must not pretend otherwise.
    """
    loan_amount = round(project_cost - margin_capital, 2)
    if loan_amount < 0:
        loan_amount = 0.0

    monthly_emi, _total_repayment, total_interest = _calculate_loan_emi(
        loan_amount=loan_amount,
        annual_interest_rate=_DEFAULT_INTEREST_RATE,
        tenure_months=_DEFAULT_REPAYMENT_MONTHS,
    )

    return FinanceInfo(
        project_cost=round(project_cost, 2),
        own_contribution=round(margin_capital, 2),
        loan_amount=loan_amount,
        # Operational fields: not available in phase 1
        monthly_revenue=0.0,
        monthly_operating_cost=0.0,
        monthly_profit=0.0,
        profit_margin=0.0,
        # Loan-structural fields computed from finance engine
        emi=monthly_emi,
        total_interest=total_interest,
        break_even=0.0,
        payback_months=_DEFAULT_REPAYMENT_MONTHS if loan_amount > 0 else 0,
        is_estimate=True,
        calculation_note=_CALCULATION_NOTE,
    )


def _build_scheme_section(
    state: str,
    district: str,
    business_category: str,
) -> SchemeInfo:
    """Run the existing deterministic recommendation engine and surface the top match.

    Maps business_category to the 'occupation' field so the recommendation
    engine can filter relevant schemes without any schema changes.
    """
    try:
        rec_request = RecommendationRequest(
            state=state,
            district=district,
            occupation=business_category,
        )
        recommendations = get_recommendations(rec_request)

        if not recommendations:
            return SchemeInfo(
                status="no_match",
                recommended_scheme=None,
                match_score=0,
                reasons=["No matching schemes found for the given inputs."],
            )

        top = recommendations[0]
        top_scheme: Dict[str, Any] = top.get("scheme", {})
        scheme_name: Optional[str] = (
            top_scheme.get("name")
            or top_scheme.get("short_name")
        )
        match_score: int = int(top.get("match_score", 0))
        reasons: List[str] = list(top.get("match_reasons", []))

        return SchemeInfo(
            status="matched",
            recommended_scheme=scheme_name,
            match_score=match_score,
            reasons=reasons,
        )

    except Exception as exc:
        logger.error(
            "Scheme recommendation failed for state=%s category=%s: %s",
            state,
            business_category,
            str(exc),
        )
        return SchemeInfo(
            status="error",
            recommended_scheme=None,
            match_score=0,
            reasons=["Scheme lookup encountered an error; please retry."],
        )


def _build_opportunity_section(
    business_category: str,
    scheme_match_score: int,
    loan_amount: float,
    project_cost: float,
) -> OpportunityInfo:
    """Derive a deterministic opportunity score from available signal.

    Scoring components (max 100):
      - scheme_match_score contributes up to 40 points (scaled).
      - Equity ratio (margin_capital / project_cost) contributes up to 30 points.
      - Business category presence (non-empty) contributes 10 points.
      - Base score: 20 points (any valid request gets this).
    """
    equity_ratio = 1.0 - (loan_amount / project_cost) if project_cost > 0 else 0.0
    equity_score = round(min(equity_ratio * 30.0, 30.0), 0)
    scheme_contrib = round((scheme_match_score / 100.0) * 40.0, 0)
    category_score = 10 if business_category.strip() else 0
    base_score = 20

    raw_score = int(base_score + category_score + equity_score + scheme_contrib)
    score = min(100, max(0, raw_score))

    level = "Pending"
    for threshold, label in _OPPORTUNITY_THRESHOLDS:
        if score >= threshold:
            level = label
            break

    reasons: List[str] = []
    if scheme_match_score > 0:
        reasons.append(
            f"A matching government scheme was found with a score of {scheme_match_score}/100."
        )
    if equity_ratio >= 0.2:
        reasons.append(
            f"Equity contribution is {round(equity_ratio * 100, 1)}% of project cost, "
            "indicating solid capital commitment."
        )
    elif equity_ratio > 0:
        reasons.append(
            f"Equity contribution is {round(equity_ratio * 100, 1)}% of project cost; "
            "consider increasing own contribution to strengthen the proposal."
        )
    if business_category.strip():
        reasons.append(f"Business category '{business_category}' is recognised.")

    return OpportunityInfo(score=score, level=level, reasons=reasons)


def _build_swot(
    business_category: str,
    state: str,
    equity_ratio: float,
    emi: float,
    loan_amount: float,
    scheme_status: str,
    scheme_name: Optional[str],
) -> SwotAnalysis:
    """Produce a deterministic SWOT from structural inputs.

    Only factual signals from the request are used — no AI inference.
    """
    strengths: List[str] = []
    weaknesses: List[str] = []
    opportunities: List[str] = []
    threats: List[str] = []

    # Strengths
    if equity_ratio >= 0.25:
        strengths.append(
            f"Strong own-capital contribution ({round(equity_ratio * 100, 1)}%) "
            "demonstrates financial commitment."
        )
    if business_category.strip():
        strengths.append(
            f"'{business_category}' is a defined rural business category with existing "
            "market demand in India."
        )

    # Weaknesses
    if equity_ratio < 0.10:
        weaknesses.append(
            "Very low own-capital contribution (<10%) increases loan dependency and default risk."
        )
    if loan_amount > 0 and emi > 0:
        weaknesses.append(
            f"Monthly EMI obligation of ₹{emi:,.2f} requires consistent revenue generation "
            "from day one."
        )
    if equity_ratio == 0.0 and loan_amount > 0:
        weaknesses.append(
            "Zero own contribution; full project cost is debt-financed — very high financial risk."
        )

    # Opportunities
    if scheme_status == "matched" and scheme_name:
        opportunities.append(
            f"Government scheme '{scheme_name}' may offer subsidised financing or grants."
        )
    opportunities.append(
        f"Rural markets in {state} present significant untapped demand for quality "
        f"{business_category.lower()} products and services."
    )
    opportunities.append(
        "Digital market linkage platforms (e-NAM, Agri-market) can extend reach beyond local geography."
    )

    # Threats
    threats.append(
        "Seasonal variation and supply-chain disruptions can affect revenue consistency."
    )
    threats.append(
        "Competition from established cooperative societies and FMCG distributors in the region."
    )
    if loan_amount > 500_000:
        threats.append(
            "High loan quantum (>₹5 lakh) increases exposure to interest-rate changes and "
            "repayment pressure during early operating months."
        )

    return SwotAnalysis(
        strengths=strengths,
        weaknesses=weaknesses,
        opportunities=opportunities,
        threats=threats,
    )


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def analyze_business(request: BusinessAnalyzeRequest) -> BusinessAnalyzeResponse:
    """Orchestrate the full business feasibility analysis.

    Order of execution:
      1. Finance section  — structural loan metrics (always deterministic, no DB)
      2. Scheme section   — deterministic scheme matching (reads Supabase)
      3. Opportunity score — derived from finance + scheme signals
      4. SWOT             — derived from structural inputs
      5. Market           — pending (no competitor DB yet)

    Args:
        request: Validated BusinessAnalyzeRequest.

    Returns:
        BusinessAnalyzeResponse with all sections populated.

    Raises:
        RuntimeError: If a critical sub-service fails and the error cannot be
                      gracefully surfaced in the relevant section.
    """
    logger.info(
        "Business analysis requested: category=%s state=%s district=%s "
        "project_cost=%.2f margin_capital=%.2f",
        request.business_category,
        request.location.state,
        request.location.district,
        request.project_cost,
        request.margin_capital,
    )

    # Validate margin does not exceed project cost
    if request.margin_capital > request.project_cost:
        raise ValueError(
            "margin_capital cannot exceed project_cost. "
            f"Got margin_capital={request.margin_capital}, project_cost={request.project_cost}."
        )

    # --- 1. Finance ---
    finance = _build_finance_section(
        project_cost=request.project_cost,
        margin_capital=request.margin_capital,
    )

    # --- 2. Scheme ---
    scheme = _build_scheme_section(
        state=request.location.state,
        district=request.location.district,
        business_category=request.business_category,
    )

    # --- 3. Market & Competitor Intelligence (Google Places API) ---
    market = get_google_places_competitor_analysis(
        location=request.location,
        business_category=request.business_category,
        radius_km=10,
    )

    # --- 4. Feasibility & Opportunity Engine ---
    opportunity = calculate_feasibility_score(
        project_cost=request.project_cost,
        margin_capital=request.margin_capital,
        loan_amount=finance.loan_amount,
        emi=finance.emi,
        business_category=request.business_category,
        location=request.location,
        scheme_info=scheme,
        market_info=market,
    )

    # --- 5. SWOT ---
    equity_ratio = (
        (request.margin_capital / request.project_cost)
        if request.project_cost > 0
        else 0.0
    )
    swot = _build_swot(
        business_category=request.business_category,
        state=request.location.state,
        equity_ratio=equity_ratio,
        emi=finance.emi,
        loan_amount=finance.loan_amount,
        scheme_status=scheme.status,
        scheme_name=scheme.recommended_scheme,
    )

    # --- Assemble response ---
    business_info = BusinessInfo(
        category=request.business_category,
        location={
            "state": request.location.state,
            "district": request.location.district,
            "village": request.location.village,
        },
    )

    logger.info(
        "Business analysis complete: category=%s opportunity_score=%d scheme_status=%s",
        request.business_category,
        opportunity.score,
        scheme.status,
    )

    return BusinessAnalyzeResponse(
        business=business_info,
        market=market,
        opportunity=opportunity,
        finance=finance,
        scheme=scheme,
        swot=swot,
    )
