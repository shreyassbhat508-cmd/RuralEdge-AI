"""Deterministic Business Feasibility and Opportunity Scoring Engine for RuralEdge.

This module provides a 100% deterministic, rule-based scoring engine for evaluating
rural business feasibility across 5 key pillars:
  1. Market potential (25% weight)
  2. Competition (20% weight)
  3. Financial feasibility (25% weight)
  4. Location / accessibility (10% weight)
  5. Affordability (20% weight)

No LLMs are used for score calculation. All scores are explainable with clear,
human-readable reasons and explicit fallback handling when data is unavailable.
"""

import logging
from typing import Dict, List, Optional, Tuple
from app.schemas.business import LocationInput, MarketInfo, OpportunityComponents, OpportunityInfo, SchemeInfo

logger = logging.getLogger(__name__)

# Weight constants (Sum = 1.00 / 100%)
WEIGHT_MARKET = 0.25
WEIGHT_COMPETITION = 0.20
WEIGHT_FINANCIAL = 0.25
WEIGHT_LOCATION = 0.10
WEIGHT_AFFORDABILITY = 0.20

# Known high-demand rural categories
HIGH_DEMAND_RURAL_CATEGORIES = {
    "dairy",
    "poultry",
    "agriculture",
    "agri-tech",
    "agritech",
    "food processing",
    "horticulture",
    "goat farming",
    "fisheries",
    "aquaculture",
    "organic farming",
    "micro-enterprise",
    "handloom",
    "handicrafts",
}

MODERATE_DEMAND_CATEGORIES = {
    "retail",
    "grocery",
    "tailoring",
    "repair shop",
    "service center",
    "transport",
    "renewable energy",
    "solar",
}


def calculate_feasibility_score(
    project_cost: float,
    margin_capital: float,
    loan_amount: float,
    emi: float,
    business_category: str,
    location: LocationInput,
    scheme_info: Optional[SchemeInfo] = None,
    market_info: Optional[MarketInfo] = None,
) -> OpportunityInfo:
    """Calculate deterministic feasibility score and component metrics.

    Returns an OpportunityInfo instance with overall score, level ('Low'|'Medium'|'High'),
    component breakdown (market, competition, financial, location, affordability),
    and explainable reasons.
    """
    reasons: List[str] = []

    # 1. Market Potential (25%)
    market_score, market_reasons = _evaluate_market_potential(
        business_category=business_category,
        scheme_info=scheme_info,
        market_info=market_info,
    )
    reasons.extend(market_reasons)

    # 2. Competition (20%)
    competition_score, competition_reasons = _evaluate_competition(
        market_info=market_info,
    )
    reasons.extend(competition_reasons)

    # 3. Financial Feasibility (25%)
    financial_score, financial_reasons = _evaluate_financial_feasibility(
        project_cost=project_cost,
        margin_capital=margin_capital,
        loan_amount=loan_amount,
    )
    reasons.extend(financial_reasons)

    # 4. Location / Accessibility (10%)
    location_score, location_reasons = _evaluate_location(
        location=location,
    )
    reasons.extend(location_reasons)

    # 5. Affordability (20%)
    affordability_score, affordability_reasons = _evaluate_affordability(
        project_cost=project_cost,
        margin_capital=margin_capital,
        loan_amount=loan_amount,
        emi=emi,
    )
    reasons.extend(affordability_reasons)

    # Calculate weighted overall score
    raw_score = (
        WEIGHT_MARKET * market_score
        + WEIGHT_COMPETITION * competition_score
        + WEIGHT_FINANCIAL * financial_score
        + WEIGHT_LOCATION * location_score
        + WEIGHT_AFFORDABILITY * affordability_score
    )

    final_score = max(0, min(100, int(round(raw_score))))

    # Classification level
    if final_score >= 75:
        level = "High"
    elif final_score >= 50:
        level = "Medium"
    else:
        level = "Low"

    components = OpportunityComponents(
        market=market_score,
        competition=competition_score,
        financial=financial_score,
        location=location_score,
        affordability=affordability_score,
    )

    logger.info(
        f"Feasibility engine score={final_score} ({level}) for category='{business_category}' "
        f"components={components.model_dump()}"
    )

    return OpportunityInfo(
        score=final_score,
        level=level,
        components=components,
        reasons=reasons,
    )


def _evaluate_market_potential(
    business_category: str,
    scheme_info: Optional[SchemeInfo],
    market_info: Optional[MarketInfo],
) -> Tuple[int, List[str]]:
    reasons = []
    category_lower = business_category.strip().lower()

    # Sector baseline demand score
    if any(cat in category_lower for cat in HIGH_DEMAND_RURAL_CATEGORIES):
        base_score = 80
        reasons.append(f"High growth potential category: {business_category}")
    elif any(cat in category_lower for cat in MODERATE_DEMAND_CATEGORIES):
        base_score = 65
        reasons.append(f"Moderate demand profile for category: {business_category}")
    else:
        base_score = 50
        reasons.append(f"Standard sector market profile for category: {business_category}")

    # Government scheme alignment bonus
    if scheme_info and scheme_info.status == "matched" and scheme_info.recommended_scheme:
        match_score = scheme_info.match_score
        if match_score >= 80:
            base_score += 15
            reasons.append(f"Strong government scheme match available (Match score: {match_score})")
        elif match_score >= 50:
            base_score += 10
            reasons.append(f"Government scheme support available (Match score: {match_score})")
    elif scheme_info and scheme_info.status == "no_match":
        reasons.append("No direct government scheme match identified")

    # Data fallback explanation if local market reach survey is pending
    if not market_info or market_info.status != "available":
        reasons.append("Market reach survey dataset pending; score computed from sector demand baseline and scheme alignment")

    score = max(0, min(100, base_score))
    return score, reasons


def _evaluate_competition(
    market_info: Optional[MarketInfo],
) -> Tuple[int, List[str]]:
    reasons = []

    if market_info and market_info.status in ("success", "available", "no_results") and market_info.competition_score is not None:
        score = market_info.competition_score
        count = market_info.competitor_count or 0
        radius = market_info.radius_km
        if count == 0:
            reasons.append(f"Low competitor density within {radius} km")
        elif count <= 2:
            reasons.append(f"Low competitor presence ({count} competitors within {radius} km)")
        elif count <= 5:
            reasons.append(f"Moderate competition ({count} competitors within {radius} km)")
        else:
            reasons.append(f"High competitor density ({count} competitors within {radius} km)")
    else:
        # Documented neutral baseline when Google Places data is unavailable
        score = 70
        msg = market_info.message if market_info and market_info.message else "Google Places data is currently unavailable."
        reasons.append(f"{msg} Applied documented baseline competition score (70).")

    return score, reasons


def _evaluate_financial_feasibility(
    project_cost: float,
    margin_capital: float,
    loan_amount: float,
) -> Tuple[int, List[str]]:
    reasons = []

    # 1. Equity Contribution Ratio (60% weight)
    equity_ratio = (margin_capital / project_cost) if project_cost > 0 else 0.0
    equity_pct = round(equity_ratio * 100, 1)

    if equity_ratio >= 0.30:
        equity_score = 95
        reasons.append(f"Strong promoter equity contribution ({equity_pct}%)")
    elif equity_ratio >= 0.20:
        equity_score = 85
        reasons.append(f"Solid promoter equity contribution ({equity_pct}%)")
    elif equity_ratio >= 0.10:
        equity_score = 70
        reasons.append(f"Moderate equity contribution ({equity_pct}%)")
    elif equity_ratio >= 0.05:
        equity_score = 50
        reasons.append(f"Low equity contribution ({equity_pct}%), high loan dependence")
    else:
        equity_score = 30
        reasons.append(f"Very low equity contribution ({equity_pct}%), high credit risk")

    # 2. Capital Scale Appropriateness (40% weight)
    if project_cost <= 5_000_000:  # <= 50 Lakhs
        scale_score = 90
        reasons.append("Loan requirement is within the recommended financing range")
    elif project_cost <= 20_000_000:  # <= 2 Crore
        scale_score = 75
        reasons.append("Moderate project scale for rural MSME credit models")
    else:
        scale_score = 55
        reasons.append("High capital project requiring institutional syndicate evaluation")

    financial_score = int(round(0.60 * equity_score + 0.40 * scale_score))
    financial_score = max(0, min(100, financial_score))

    return financial_score, reasons


def _evaluate_location(
    location: LocationInput,
) -> Tuple[int, List[str]]:
    reasons = []

    if location.village and location.village.strip():
        score = 85
        reasons.append(f"Village-level location ({location.village}) identified for Gram Panchayat benefits")
    elif location.district and location.district.strip():
        score = 75
        reasons.append(f"District-level location ({location.district}, {location.state}) identified")
    else:
        score = 65
        reasons.append(f"State-level location ({location.state}) identified")

    reasons.append("Detailed transport/accessibility dataset unavailable; location score based on administrative tier")

    return score, reasons


def _evaluate_affordability(
    project_cost: float,
    margin_capital: float,
    loan_amount: float,
    emi: float,
) -> Tuple[int, List[str]]:
    reasons = []

    if loan_amount <= 0:
        score = 100
        reasons.append("100% self-funded project with zero debt service liability")
        return score, reasons

    # Debt service ratio relative to project capital
    annual_emi = emi * 12
    debt_service_ratio = (annual_emi / project_cost) if project_cost > 0 else 0.0

    equity_ratio = (margin_capital / project_cost) if project_cost > 0 else 0.0
    equity_score = min(100, int(round(equity_ratio * 100 * 2.5)))  # 30% equity -> 75, 40% equity -> 100

    if debt_service_ratio <= 0.15:
        emi_score = 90
        reasons.append("Manageable monthly EMI debt service burden")
    elif debt_service_ratio <= 0.25:
        emi_score = 70
        reasons.append("Moderate monthly debt servicing requirement")
    else:
        emi_score = 45
        reasons.append("High monthly EMI debt service burden relative to project scale")

    affordability_score = int(round(0.50 * equity_score + 0.50 * emi_score))
    affordability_score = max(0, min(100, affordability_score))

    return affordability_score, reasons
