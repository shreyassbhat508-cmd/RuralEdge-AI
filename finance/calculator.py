"""Calculator module for the RuralEdge Finance Engine.

Implements deterministic financial calculations for capital structure, loan EMI repayment,
monthly/annual profitability, operating break-even revenue, and estimated investment payback
(Phase F1), plus monthly/annual cash flow, debt-service break-even, break-even gap and status
indicators, cash-flow status, and cumulative cash-flow projection (Phase F2).

Monetary Rounding Policy
------------------------
All monetary output values are rounded to 2 decimal places at each computational
boundary. Intermediate unrounded values are used within a single function only
and are never propagated to downstream calculations.

EMI Rounding Note
-----------------
The standard reducing-balance EMI formula produces an irrational result in general.
The EMI is rounded to 2 decimal places before being used in any downstream
calculation (monthly_total_cost, monthly_cash_flow, debt-service break-even, etc.)
to ensure a consistent monetary representation throughout.

Payback Period Note
-------------------
estimated_payback_months is a simple, undiscounted payback estimate:
    total_project_cost / monthly_cash_flow
It is not an investment-grade discounted cash-flow (DCF) calculation.
It is only meaningful when monthly_cash_flow > 0.
"""

from typing import Dict, Optional, Tuple

from finance.models import (
    FinanceInput,
    FinanceResult,
    FinancialAssessment,
    MORATORIUM_REPAYMENT_NOTE,
    ProjectInput,
    ProjectRequirement,
    SchemeFinance,
    SchemeFinancingResult,
)
from finance.validators import validate_finance_input, validate_project_input, validate_scheme_finance


# ---------------------------------------------------------------------------
# Private helpers – F1
# ---------------------------------------------------------------------------

def _calculate_loan_emi(
    loan_amount: float,
    annual_interest_rate: float,
    tenure_months: int,
) -> Tuple[float, float, float]:
    """Calculates monthly EMI, total repayment, and total interest.

    Args:
        loan_amount: Principal loan amount.
        annual_interest_rate: Annual interest rate in percent (e.g. 10.0 for 10 %).
        tenure_months: Loan tenure in months.

    Returns:
        Tuple (monthly_emi, total_repayment, total_interest), all rounded to 2 dp.
    """
    if loan_amount <= 0 or tenure_months <= 0:
        return 0.0, 0.0, 0.0

    monthly_rate = annual_interest_rate / 12.0 / 100.0

    if monthly_rate > 0:
        # Standard reducing-balance EMI: P * r * (1+r)^n / ((1+r)^n - 1)
        compound_factor = (1.0 + monthly_rate) ** tenure_months
        raw_emi = (loan_amount * monthly_rate * compound_factor) / (compound_factor - 1.0)
    else:
        # Zero-interest loan
        raw_emi = loan_amount / tenure_months

    monthly_emi = round(raw_emi, 2)
    total_repayment = round(monthly_emi * tenure_months, 2)
    total_interest = round(total_repayment - loan_amount, 2)

    return monthly_emi, total_repayment, total_interest


def _calculate_capital_structure(
    total_project_cost: float,
    own_contribution: float,
    loan_amount: float,
) -> Tuple[float, float, float, float]:
    """Calculates loan required, capital gap, own-contribution %, and financing %.

    Returns:
        Tuple (loan_required, capital_gap, own_contribution_pct, financing_pct).
    """
    loan_required = loan_amount
    capital_gap = round(total_project_cost - own_contribution - loan_amount, 2)

    if total_project_cost > 0:
        own_pct = round((own_contribution / total_project_cost) * 100.0, 2)
        fin_pct = round((loan_amount / total_project_cost) * 100.0, 2)
    else:
        own_pct = 0.0
        fin_pct = 0.0

    return loan_required, capital_gap, own_pct, fin_pct


def _calculate_profitability(
    monthly_revenue: float,
    monthly_operating_cost: float,
    monthly_fixed_cost: float,
    monthly_emi: float,
) -> Tuple[float, float, float, float, float]:
    """Calculates total monthly cost, monthly profit, annual revenue, annual profit, and profit margin.

    Returns:
        Tuple (monthly_total_cost, monthly_profit, annual_revenue, annual_profit, profit_margin_pct).
    """
    monthly_total_cost = round(monthly_operating_cost + monthly_fixed_cost + monthly_emi, 2)
    monthly_profit = round(monthly_revenue - monthly_total_cost, 2)
    annual_revenue = round(monthly_revenue * 12.0, 2)
    annual_profit = round(monthly_profit * 12.0, 2)

    if monthly_revenue > 0:
        margin_pct = round((monthly_profit / monthly_revenue) * 100.0, 2)
    else:
        margin_pct = 0.0

    return monthly_total_cost, monthly_profit, annual_revenue, annual_profit, margin_pct


def _calculate_operating_break_even(
    monthly_revenue: float,
    monthly_operating_cost: float,
    monthly_fixed_cost: float,
) -> Optional[float]:
    """Calculates operating break-even revenue based on contribution margin ratio.

    Operating break-even covers only fixed costs (not EMI).
    Formula: monthly_fixed_cost / contribution_margin_ratio

    Returns:
        Rounded break-even revenue, or None when not calculable.
    """
    if monthly_revenue <= 0:
        return None

    contribution_margin = monthly_revenue - monthly_operating_cost
    contribution_margin_ratio = contribution_margin / monthly_revenue

    if contribution_margin_ratio <= 0:
        return None

    return round(monthly_fixed_cost / contribution_margin_ratio, 2)


def _calculate_payback_period(
    total_project_cost: float,
    monthly_cash_flow: float,
) -> Optional[float]:
    """Calculates the estimated simple payback period in months.

    This is a simple undiscounted payback estimate (total_project_cost / monthly_cash_flow).
    It is NOT an investment-grade DCF calculation.

    Returns:
        Rounded payback months when monthly_cash_flow > 0 and project cost > 0, else None.
    """
    if monthly_cash_flow > 0 and total_project_cost > 0:
        return round(total_project_cost / monthly_cash_flow, 2)
    return None


# ---------------------------------------------------------------------------
# Private helpers – F2
# ---------------------------------------------------------------------------

def _get_contribution_margin_ratio(
    monthly_revenue: float,
    monthly_operating_cost: float,
) -> Optional[float]:
    """Returns the contribution margin ratio, or None when not calculable.

    contribution_margin_ratio = (monthly_revenue - monthly_operating_cost) / monthly_revenue

    Returns None when monthly_revenue <= 0 or the resulting ratio is <= 0 (i.e.
    operating costs equal or exceed revenue, making break-even analysis meaningless).
    """
    if monthly_revenue <= 0:
        return None
    ratio = (monthly_revenue - monthly_operating_cost) / monthly_revenue
    return ratio if ratio > 0 else None


def _calculate_cash_flow(
    monthly_revenue: float,
    monthly_operating_cost: float,
    monthly_fixed_cost: float,
    monthly_emi: float,
) -> Tuple[float, float]:
    """Calculates monthly and annual cash flow.

    monthly_cash_flow = monthly_revenue
                        - monthly_operating_cost
                        - monthly_fixed_cost
                        - monthly_emi

    EMI is already rounded to 2 dp before entering this function, ensuring
    no hidden floating-point remainder is carried forward.

    Returns:
        Tuple (monthly_cash_flow, annual_cash_flow), both rounded to 2 dp.
    """
    monthly_cf = round(monthly_revenue - monthly_operating_cost - monthly_fixed_cost - monthly_emi, 2)
    annual_cf = round(monthly_cf * 12.0, 2)
    return monthly_cf, annual_cf


def _calculate_debt_service_break_even(
    monthly_fixed_cost: float,
    monthly_emi: float,
    cm_ratio: Optional[float],
) -> Optional[float]:
    """Calculates debt-service break-even revenue.

    This is the revenue required to cover both fixed costs AND loan EMI, using the
    same contribution margin ratio as the operating break-even.

    Formula: (monthly_fixed_cost + monthly_emi) / contribution_margin_ratio

    Distinction from operating break-even:
        - Operating break-even covers fixed costs only (no EMI).
        - Debt-service break-even covers fixed costs PLUS loan repayment (EMI).
        - Debt-service break-even >= operating break-even for any positive EMI.

    Returns:
        Rounded break-even revenue, or None when cm_ratio is None.
    """
    if cm_ratio is None:
        return None
    return round((monthly_fixed_cost + monthly_emi) / cm_ratio, 2)


def _calculate_break_even_gaps(
    monthly_revenue: float,
    operating_be: Optional[float],
    debt_service_be: Optional[float],
) -> Tuple[Optional[float], Optional[float]]:
    """Calculates break-even gaps for operating and debt-service break-evens.

    Gap = monthly_revenue - break_even_revenue
    Positive: revenue is above break-even.
    Negative: revenue is below break-even.
    None:     break-even is not calculable.

    Returns:
        Tuple (operating_break_even_gap, debt_service_break_even_gap).
    """
    op_gap = round(monthly_revenue - operating_be, 2) if operating_be is not None else None
    ds_gap = round(monthly_revenue - debt_service_be, 2) if debt_service_be is not None else None
    return op_gap, ds_gap


def _determine_break_even_status(
    monthly_revenue: float,
    break_even_revenue: Optional[float],
) -> str:
    """Returns a deterministic break-even status string.

    Returns:
        "not_calculable"  – break-even revenue cannot be determined.
        "above_break_even" – monthly_revenue >= break_even_revenue.
        "below_break_even" – monthly_revenue < break_even_revenue.
    """
    if break_even_revenue is None:
        return "not_calculable"
    return "above_break_even" if monthly_revenue >= break_even_revenue else "below_break_even"


def _determine_cash_flow_status(monthly_cash_flow: float) -> str:
    """Returns a deterministic cash-flow status string.

    Returns:
        "positive" – monthly_cash_flow > 0.
        "neutral"  – monthly_cash_flow == 0.
        "negative" – monthly_cash_flow < 0.
    """
    if monthly_cash_flow > 0:
        return "positive"
    if monthly_cash_flow < 0:
        return "negative"
    return "neutral"


# ---------------------------------------------------------------------------
# Public helper – F2
# ---------------------------------------------------------------------------

def calculate_cumulative_cash_flow(monthly_cash_flow: float, months: int) -> Dict[int, float]:
    """Calculates cumulative cash flow for each month over a specified period.

    Assumes a constant monthly_cash_flow with no seasonal variation.
    Each month's cumulative value is rounded to 2 decimal places independently
    to avoid floating-point drift across long projection horizons.

    Args:
        monthly_cash_flow: Constant estimated monthly cash flow (may be negative).
        months: Number of months to project (must be >= 0).

    Returns:
        Dict mapping month number (1-indexed) to cumulative cash flow at that month.
        Returns an empty dict when months == 0.

    Example:
        calculate_cumulative_cash_flow(10000.0, 3)
        → {1: 10000.0, 2: 20000.0, 3: 30000.0}
    """
    if months <= 0:
        return {}

    result: Dict[int, float] = {}
    cumulative = 0.0
    for month in range(1, months + 1):
        cumulative = round(cumulative + monthly_cash_flow, 2)
        result[month] = cumulative
    return result


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def calculate_financials(finance_input: FinanceInput) -> FinanceResult:
    """Main entry point for computing comprehensive project financial metrics.

    Executes the full F1 + F2 calculation pipeline in a deterministic sequence:
        1. Input validation
        2. Capital structure
        3. Loan EMI and repayment schedule
        4. Profitability (monthly/annual)
        5. Operating break-even revenue
        6. F2 – Cash flow (monthly / annual)
        7. F2 – Contribution margin ratio (shared by both break-even calculations)
        8. F2 – Debt-service break-even revenue
        9. F2 – Break-even gaps and status indicators
        10. F2 – Cash-flow status
        11. Payback period (uses monthly_cash_flow)
        12. F2 – Cumulative cash flow projection

    Args:
        finance_input: Input financial parameters DTO.

    Returns:
        FinanceResult containing all F1 and F2 computed metrics.

    Raises:
        FinanceValidationError: If input parameters violate validation constraints.
    """
    # 1. Validate
    validate_finance_input(finance_input)

    # 2. Capital Structure
    loan_required, capital_gap, own_pct, fin_pct = _calculate_capital_structure(
        total_project_cost=finance_input.total_project_cost,
        own_contribution=finance_input.own_contribution,
        loan_amount=finance_input.loan_amount,
    )

    # 3. Loan EMI & Repayment (monthly_emi is rounded to 2 dp here and used as-is downstream)
    monthly_emi, total_repayment, total_interest = _calculate_loan_emi(
        loan_amount=finance_input.loan_amount,
        annual_interest_rate=finance_input.annual_interest_rate,
        tenure_months=finance_input.loan_tenure_months,
    )

    # 4. Profitability
    monthly_total_cost, monthly_profit, annual_revenue, annual_profit, profit_margin_pct = (
        _calculate_profitability(
            monthly_revenue=finance_input.monthly_revenue,
            monthly_operating_cost=finance_input.monthly_operating_cost,
            monthly_fixed_cost=finance_input.monthly_fixed_cost,
            monthly_emi=monthly_emi,
        )
    )

    # 5. Operating Break-Even Revenue (F1 field: break_even_revenue)
    break_even_revenue = _calculate_operating_break_even(
        monthly_revenue=finance_input.monthly_revenue,
        monthly_operating_cost=finance_input.monthly_operating_cost,
        monthly_fixed_cost=finance_input.monthly_fixed_cost,
    )

    # 6. F2 – Monthly / Annual Cash Flow
    monthly_cash_flow, annual_cash_flow = _calculate_cash_flow(
        monthly_revenue=finance_input.monthly_revenue,
        monthly_operating_cost=finance_input.monthly_operating_cost,
        monthly_fixed_cost=finance_input.monthly_fixed_cost,
        monthly_emi=monthly_emi,
    )

    # 7. F2 – Contribution Margin Ratio (shared denominator for both break-evens)
    cm_ratio = _get_contribution_margin_ratio(
        monthly_revenue=finance_input.monthly_revenue,
        monthly_operating_cost=finance_input.monthly_operating_cost,
    )

    # 8. F2 – Debt-Service Break-Even Revenue
    debt_service_be = _calculate_debt_service_break_even(
        monthly_fixed_cost=finance_input.monthly_fixed_cost,
        monthly_emi=monthly_emi,
        cm_ratio=cm_ratio,
    )

    # 9. F2 – Break-Even Gaps and Statuses
    op_be_gap, ds_be_gap = _calculate_break_even_gaps(
        monthly_revenue=finance_input.monthly_revenue,
        operating_be=break_even_revenue,
        debt_service_be=debt_service_be,
    )
    op_be_status = _determine_break_even_status(finance_input.monthly_revenue, break_even_revenue)
    ds_be_status = _determine_break_even_status(finance_input.monthly_revenue, debt_service_be)

    # 10. F2 – Cash-Flow Status
    cf_status = _determine_cash_flow_status(monthly_cash_flow)

    # 11. Payback Period (uses monthly_cash_flow; returns None when cash flow <= 0)
    estimated_payback_months = _calculate_payback_period(
        total_project_cost=finance_input.total_project_cost,
        monthly_cash_flow=monthly_cash_flow,
    )

    # 12. F2 – Cumulative Cash Flow Projection
    projection_months = finance_input.loan_tenure_months if finance_input.loan_tenure_months > 0 else 12
    cumulative_cf = calculate_cumulative_cash_flow(monthly_cash_flow, projection_months)

    return FinanceResult(
        # F1: Capital Structure
        business_name=finance_input.business_name,
        total_project_cost=finance_input.total_project_cost,
        own_contribution=finance_input.own_contribution,
        loan_amount=finance_input.loan_amount,
        loan_required=loan_required,
        capital_gap=capital_gap,
        own_contribution_percentage=own_pct,
        financing_percentage=fin_pct,
        # F1: Loan Repayment
        monthly_emi=monthly_emi,
        total_repayment=total_repayment,
        total_interest=total_interest,
        # F1: Profitability
        monthly_revenue=finance_input.monthly_revenue,
        monthly_operating_cost=finance_input.monthly_operating_cost,
        monthly_fixed_cost=finance_input.monthly_fixed_cost,
        monthly_total_cost=monthly_total_cost,
        monthly_profit=monthly_profit,
        annual_revenue=annual_revenue,
        annual_profit=annual_profit,
        profit_margin_percentage=profit_margin_pct,
        # F1: Operating Break-Even and Payback
        break_even_revenue=break_even_revenue,
        estimated_payback_months=estimated_payback_months,
        # F2: Cash Flow
        monthly_cash_flow=monthly_cash_flow,
        annual_cash_flow=annual_cash_flow,
        # F2: Debt-Service Break-Even
        debt_service_break_even_revenue=debt_service_be,
        # F2: Gaps
        operating_break_even_gap=op_be_gap,
        debt_service_break_even_gap=ds_be_gap,
        # F2: Statuses
        operating_break_even_status=op_be_status,
        debt_service_break_even_status=ds_be_status,
        cash_flow_status=cf_status,
        # F2: Cumulative
        cumulative_cash_flow=cumulative_cf,
    )


# ===========================================================================
# 4-Step Architecture — Step 1: Project Requirement
# ===========================================================================

def calculate_project_requirement(project_input: ProjectInput) -> ProjectRequirement:
    """Step 1 — Computes total project cost and funding requirement from cost components.

    project_cost = fixed_asset_cost + setup_cost + initial_inventory_cost
                   + initial_working_capital

    Working capital is an explicit, single input value.  The engine does NOT
    multiply it by any fixed number of months — that assumption is left to the caller.

    loan_required = max(0, project_cost − own_contribution)

    A surplus own contribution (own_contribution > project_cost) is not an error;
    it is clamped to loan_required = 0 and reported as own_contribution_surplus.

    Args:
        project_input: ProjectInput DTO containing cost components and own contribution.

    Returns:
        ProjectRequirement with computed project_cost and loan_required.

    Raises:
        FinanceValidationError: If any cost component or contribution is negative.
    """
    validate_project_input(project_input)

    project_cost = round(
        project_input.fixed_asset_cost
        + project_input.setup_cost
        + project_input.initial_inventory_cost
        + project_input.initial_working_capital,
        2,
    )

    raw_loan_required = project_cost - project_input.own_contribution
    loan_required = round(max(0.0, raw_loan_required), 2)
    own_contribution_surplus = round(max(0.0, -raw_loan_required), 2)

    return ProjectRequirement(
        business_name=project_input.business_name,
        business_category=project_input.business_category,
        location=project_input.location,
        fixed_asset_cost=project_input.fixed_asset_cost,
        setup_cost=project_input.setup_cost,
        initial_inventory_cost=project_input.initial_inventory_cost,
        initial_working_capital=project_input.initial_working_capital,
        project_cost=project_cost,
        own_contribution=project_input.own_contribution,
        loan_required=loan_required,
        own_contribution_surplus=own_contribution_surplus,
    )


# ===========================================================================
# 4-Step Architecture — Step 2: Scheme Financing
# ===========================================================================

def apply_scheme_financing(
    loan_required: float,
    scheme_finance: Optional[SchemeFinance] = None,
) -> SchemeFinancingResult:
    """Step 2 — Applies government scheme loan cap to the required loan amount.

    When a scheme is supplied:
        applicable_loan = min(loan_required, scheme.maximum_loan_amount)
        funding_gap     = loan_required − applicable_loan  (≥ 0)
        has_confirmed_financing = True

    When no scheme is supplied:
        The engine does NOT invent interest rate, tenure, or loan cap.
        applicable_loan = loan_required  (full requirement is noted but unconfirmed)
        funding_gap     = 0  (no cap was applied)
        interest_rate, tenure_months, scheme_loan_cap = None
        has_confirmed_financing = False

    Distinction between no-scheme and no-gap:
        A has_confirmed_financing = False result with loan_required > 0 signals
        that financing is needed but no scheme has been applied yet.  This drives
        financial_status = "modify" in Step 4.

    Args:
        loan_required: The loan amount required from Step 1.
        scheme_finance: Optional SchemeFinance DTO. Pass None when no scheme is available.

    Returns:
        SchemeFinancingResult with applicable loan and gap.

    Raises:
        FinanceValidationError: If scheme_finance parameters violate constraints.
    """
    if scheme_finance is None:
        return SchemeFinancingResult(
            scheme_name=None,
            requested_loan=loan_required,
            scheme_loan_cap=None,
            applicable_loan=loan_required,
            funding_gap=0.0,
            interest_rate=None,
            tenure_months=None,
            moratorium_months=0,
            has_confirmed_financing=False,
        )

    validate_scheme_finance(scheme_finance)

    applicable_loan = round(min(loan_required, scheme_finance.maximum_loan_amount), 2)
    funding_gap = round(max(0.0, loan_required - applicable_loan), 2)

    return SchemeFinancingResult(
        scheme_name=scheme_finance.scheme_name,
        requested_loan=loan_required,
        scheme_loan_cap=scheme_finance.maximum_loan_amount,
        applicable_loan=applicable_loan,
        funding_gap=funding_gap,
        interest_rate=scheme_finance.interest_rate,
        tenure_months=scheme_finance.tenure_months,
        moratorium_months=scheme_finance.moratorium_months,
        has_confirmed_financing=True,
    )


# ---------------------------------------------------------------------------
# Private helper – Step 4 feasibility determination
# ---------------------------------------------------------------------------

def _determine_financial_status(
    funding_gap: float,
    monthly_cash_flow: float,
    has_confirmed_financing: bool,
    loan_required: float,
) -> str:
    """Determines deterministic financial feasibility status.

    Priority order (most severe wins):
        1. monthly_cash_flow <= 0                    → "not_feasible"
        2. funding_gap > 0                            → "modify"
        3. no confirmed financing AND loan needed     → "modify"
        4. otherwise                                  → "feasible"

    This is a feasibility assessment only.
    It does NOT constitute credit approval or guarantee of success.

    Returns:
        "not_feasible" | "modify" | "feasible"
    """
    if monthly_cash_flow <= 0:
        return "not_feasible"
    if funding_gap > 0:
        return "modify"
    if not has_confirmed_financing and loan_required > 0:
        return "modify"
    return "feasible"


# ===========================================================================
# 4-Step Architecture — Main Entry Point
# ===========================================================================

def calculate_financial_assessment(
    project_input: ProjectInput,
    scheme_finance: Optional[SchemeFinance] = None,
) -> FinancialAssessment:
    """Main entry point for the 4-step financial assessment pipeline.

    Steps executed in order:
        1. calculate_project_requirement  — project cost and loan requirement.
        2. apply_scheme_financing         — scheme loan cap and funding gap.
        3. Repayment and profitability    — EMI, cash flow, break-even (reuses F1/F2 helpers).
        4. _determine_financial_status    — feasibility classification.

    When scheme_finance is None:
        - No loan terms are invented.
        - EMI is 0 (cannot be computed without rate and tenure).
        - financial_status is "modify" when loan_required > 0, because financing
          is needed but no scheme has confirmed the terms.

    Moratorium:
        moratorium_months is stored and surfaced in the result.
        Repayment scheduling DURING the moratorium period is NOT calculated —
        see moratorium_repayment_note in the returned FinancialAssessment.

    Args:
        project_input: Business cost components and operational parameters.
        scheme_finance: Optional scheme financing terms. Pass None when not yet available.

    Returns:
        FinancialAssessment with all 4 steps populated.

    Raises:
        FinanceValidationError: If project_input or scheme_finance violate constraints.
    """
    # Step 1 — Project Requirement
    req = calculate_project_requirement(project_input)

    # Step 2 — Scheme Financing
    financing = apply_scheme_financing(req.loan_required, scheme_finance)

    # Step 3a — Loan EMI and Repayment
    # When no scheme is supplied, interest_rate and tenure_months are None.
    # _calculate_loan_emi safely returns (0.0, 0.0, 0.0) when tenure_months <= 0.
    interest_rate = financing.interest_rate if financing.interest_rate is not None else 0.0
    tenure_months = financing.tenure_months if financing.tenure_months is not None else 0

    monthly_emi, total_repayment, total_interest = _calculate_loan_emi(
        loan_amount=financing.applicable_loan,
        annual_interest_rate=interest_rate,
        tenure_months=tenure_months,
    )

    # Step 3b — Profitability
    monthly_total_cost, monthly_profit, _annual_revenue, _annual_profit, profit_margin_pct = (
        _calculate_profitability(
            monthly_revenue=project_input.expected_monthly_revenue,
            monthly_operating_cost=project_input.expected_monthly_operating_cost,
            monthly_fixed_cost=project_input.expected_monthly_fixed_cost,
            monthly_emi=monthly_emi,
        )
    )

    # Step 3c — Cash Flow (F2 calculation; monthly_cash_flow == monthly_profit)
    monthly_cash_flow, annual_cash_flow = _calculate_cash_flow(
        monthly_revenue=project_input.expected_monthly_revenue,
        monthly_operating_cost=project_input.expected_monthly_operating_cost,
        monthly_fixed_cost=project_input.expected_monthly_fixed_cost,
        monthly_emi=monthly_emi,
    )

    # Step 3d — Break-Even Analysis
    operating_be = _calculate_operating_break_even(
        monthly_revenue=project_input.expected_monthly_revenue,
        monthly_operating_cost=project_input.expected_monthly_operating_cost,
        monthly_fixed_cost=project_input.expected_monthly_fixed_cost,
    )

    cm_ratio = _get_contribution_margin_ratio(
        monthly_revenue=project_input.expected_monthly_revenue,
        monthly_operating_cost=project_input.expected_monthly_operating_cost,
    )

    debt_service_be = _calculate_debt_service_break_even(
        monthly_fixed_cost=project_input.expected_monthly_fixed_cost,
        monthly_emi=monthly_emi,
        cm_ratio=cm_ratio,
    )

    # Step 3e — Estimated Simple Payback Period
    estimated_payback = _calculate_payback_period(
        total_project_cost=req.project_cost,
        monthly_cash_flow=monthly_cash_flow,
    )

    # Step 4 — Financial Feasibility
    financial_status = _determine_financial_status(
        funding_gap=financing.funding_gap,
        monthly_cash_flow=monthly_cash_flow,
        has_confirmed_financing=financing.has_confirmed_financing,
        loan_required=req.loan_required,
    )

    return FinancialAssessment(
        # Step 1: Project Requirement
        business_name=req.business_name,
        business_category=req.business_category,
        location=req.location,
        project_cost=req.project_cost,
        own_contribution=req.own_contribution,
        own_contribution_surplus=req.own_contribution_surplus,
        loan_required=req.loan_required,
        # Step 2: Scheme Financing
        funding_gap=financing.funding_gap,
        scheme_name=financing.scheme_name,
        scheme_loan_cap=financing.scheme_loan_cap,
        applicable_loan=financing.applicable_loan,
        interest_rate=financing.interest_rate,
        tenure_months=financing.tenure_months,
        moratorium_months=financing.moratorium_months,
        moratorium_repayment_note=MORATORIUM_REPAYMENT_NOTE,
        # Step 3: Repayment
        monthly_emi=monthly_emi,
        total_repayment=total_repayment,
        total_interest=total_interest,
        # Step 3: Profitability and Cash Flow
        monthly_revenue=project_input.expected_monthly_revenue,
        monthly_operating_cost=project_input.expected_monthly_operating_cost,
        monthly_fixed_cost=project_input.expected_monthly_fixed_cost,
        monthly_total_cost=monthly_total_cost,
        monthly_cash_flow=monthly_cash_flow,
        annual_cash_flow=annual_cash_flow,
        profit_margin_percentage=profit_margin_pct,
        operating_break_even_revenue=operating_be,
        debt_service_break_even_revenue=debt_service_be,
        estimated_payback_months=estimated_payback,
        # Step 4: Feasibility
        financial_status=financial_status,
    )
