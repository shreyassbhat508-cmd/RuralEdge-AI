"""Models module for the RuralEdge Finance Engine.

Defines input and output data transfer objects using Python dataclasses.

Legacy (F1/F2)
--------------
FinanceInput, FinanceResult — used by calculate_financials(). Preserved unchanged.

4-Step Architecture
-------------------
ProjectInput         — business cost components and operational parameters.
SchemeFinance        — government scheme financing terms supplied by the caller.
ProjectRequirement   — Step 1 output: computed project cost and loan requirement.
SchemeFinancingResult — Step 2 output: scheme-applied financing after cap enforcement.
FinancialAssessment  — Combined Step 1–4 result: repayment, profitability, feasibility.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional


# ---------------------------------------------------------------------------
# Shared constant
# ---------------------------------------------------------------------------

MORATORIUM_REPAYMENT_NOTE: str = (
    "Repayment scheduling during the moratorium period is not yet implemented. "
    "Different government schemes apply different rules (e.g., interest accrual, "
    "interest subvention, or complete grace periods during moratorium). "
    "Moratorium repayment handling will be supported in a future version of this engine."
)


# ---------------------------------------------------------------------------
# Legacy F1 / F2 models — DO NOT MODIFY
# ---------------------------------------------------------------------------

@dataclass
class FinanceInput:
    """Input model representing project and operational financial parameters."""
    business_name: str
    total_project_cost: float
    own_contribution: float
    loan_amount: float
    annual_interest_rate: float
    loan_tenure_months: int
    monthly_revenue: float
    monthly_operating_cost: float
    monthly_fixed_cost: float
    working_capital: float = 0.0


@dataclass
class FinanceResult:
    """Output model containing calculated capital structure, loan repayment,
    profitability, and cash-flow analysis metrics.

    F1 fields
    ---------
    Capital structure: total_project_cost, own_contribution, loan_amount, loan_required,
        capital_gap, own_contribution_percentage, financing_percentage.
    Loan repayment: monthly_emi, total_repayment, total_interest.
    Profitability: monthly_revenue, monthly_operating_cost, monthly_fixed_cost,
        monthly_total_cost, monthly_profit, annual_revenue, annual_profit,
        profit_margin_percentage.
    Break-even (operating): break_even_revenue.
    Payback: estimated_payback_months.

    F2 fields
    ---------
    Cash flow: monthly_cash_flow, annual_cash_flow.
    Debt-service break-even: debt_service_break_even_revenue.
    Break-even gaps: operating_break_even_gap, debt_service_break_even_gap.
    Statuses: operating_break_even_status, debt_service_break_even_status, cash_flow_status.
    Cumulative: cumulative_cash_flow (Dict keyed by month number starting at 1).

    Note: monthly_cash_flow and monthly_profit are computed from the same revenue/cost
    components and will be equal. They are retained as separate fields because
    monthly_profit represents accounting profitability while monthly_cash_flow represents
    the estimated cash available after all operating outflows including debt service.
    """

    # --- F1: Capital Structure ---
    business_name: str
    total_project_cost: float
    own_contribution: float
    loan_amount: float
    loan_required: float
    capital_gap: float
    own_contribution_percentage: float
    financing_percentage: float

    # --- F1: Loan Repayment ---
    monthly_emi: float
    total_repayment: float
    total_interest: float

    # --- F1: Profitability ---
    monthly_revenue: float
    monthly_operating_cost: float
    monthly_fixed_cost: float
    monthly_total_cost: float
    monthly_profit: float
    annual_revenue: float
    annual_profit: float
    profit_margin_percentage: float

    # --- F1: Operating Break-Even and Payback ---
    break_even_revenue: Optional[float]
    estimated_payback_months: Optional[float]

    # --- F2: Cash Flow ---
    monthly_cash_flow: float
    annual_cash_flow: float

    # --- F2: Debt-Service Break-Even ---
    debt_service_break_even_revenue: Optional[float]

    # --- F2: Break-Even Gaps ---
    # Positive: revenue is above break-even. Negative: revenue is below break-even.
    # None when the corresponding break-even revenue is None (not calculable).
    operating_break_even_gap: Optional[float]
    debt_service_break_even_gap: Optional[float]

    # --- F2: Statuses ---
    # operating_break_even_status: "above_break_even" | "below_break_even" | "not_calculable"
    # debt_service_break_even_status: "above_break_even" | "below_break_even" | "not_calculable"
    # cash_flow_status: "positive" | "neutral" | "negative"
    operating_break_even_status: str
    debt_service_break_even_status: str
    cash_flow_status: str

    # --- F2: Cumulative Cash Flow ---
    # Dict[month_number, cumulative_cash_flow_value].
    # Computed over loan_tenure_months (or 12 months when tenure is zero).
    cumulative_cash_flow: Dict[int, float] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# 4-Step Architecture models
# ---------------------------------------------------------------------------

@dataclass
class ProjectInput:
    """Input model for the 4-step financial assessment pipeline.

    The project cost is computed from its components (Step 1) rather than
    accepted as a single lump-sum input.  This ensures the engine understands
    how the project cost is structured and avoids working-capital double-counting.

    Working capital is an explicit, single input value (initial_working_capital).
    The engine does not assume a fixed number of working-capital months.
    """

    # Business identification
    business_name: str
    business_category: str = ""
    location: str = ""

    # Project cost components (Step 1)
    # project_cost = fixed_asset_cost + setup_cost + initial_inventory_cost + initial_working_capital
    fixed_asset_cost: float = 0.0
    setup_cost: float = 0.0
    initial_inventory_cost: float = 0.0
    initial_working_capital: float = 0.0   # explicit value; not multiplied by any month count
    own_contribution: float = 0.0

    # Business operations (Step 3)
    expected_monthly_revenue: float = 0.0
    expected_monthly_operating_cost: float = 0.0
    expected_monthly_fixed_cost: float = 0.0


@dataclass
class SchemeFinance:
    """Government scheme financing parameters supplied for Step 2.

    The caller (backend / scheme router) is responsible for populating this
    object from the government scheme data ingestion pipeline.  The finance
    engine does NOT look up scheme terms itself — it only applies the terms
    it is given.

    moratorium_months stores the grace period duration.  Repayment behaviour
    during the moratorium is scheme-specific and is NOT calculated here;
    see MORATORIUM_REPAYMENT_NOTE.
    """
    scheme_name: str
    maximum_loan_amount: float        # scheme loan cap (₹)
    interest_rate: float              # annual interest rate in percent (e.g. 7.0 for 7 %)
    tenure_months: int                # repayment tenure in months (excluding moratorium)
    moratorium_months: int = 0        # grace period; repayment impact is future work


@dataclass
class ProjectRequirement:
    """Step 1 result: computed project cost and funding requirement.

    loan_required = max(0, project_cost − own_contribution).
    Negative loan requirements (surplus own contribution) are clamped to 0
    and reported separately as own_contribution_surplus.
    """
    business_name: str
    business_category: str
    location: str

    # Cost components (passed through for auditability)
    fixed_asset_cost: float
    setup_cost: float
    initial_inventory_cost: float
    initial_working_capital: float

    # Computed
    project_cost: float               # sum of all cost components
    own_contribution: float
    loan_required: float              # max(0, project_cost − own_contribution)
    own_contribution_surplus: float   # max(0, own_contribution − project_cost); 0 in most cases


@dataclass
class SchemeFinancingResult:
    """Step 2 result: financing terms after scheme loan-cap enforcement.

    When no scheme is supplied:
        - scheme_name, scheme_loan_cap, interest_rate, tenure_months are all None.
        - applicable_loan = requested_loan (full requirement is noted but unconfirmed).
        - funding_gap = 0 (no cap was applied).
        - has_confirmed_financing = False.

    When a scheme is supplied:
        - applicable_loan = min(requested_loan, scheme.maximum_loan_amount).
        - funding_gap = requested_loan − applicable_loan (≥ 0).
        - has_confirmed_financing = True.
    """
    scheme_name: Optional[str]
    requested_loan: float
    scheme_loan_cap: Optional[float]
    applicable_loan: float
    funding_gap: float
    interest_rate: Optional[float]
    tenure_months: Optional[int]
    moratorium_months: int
    has_confirmed_financing: bool     # True only when a scheme with full terms is applied


@dataclass
class FinancialAssessment:
    """Combined output from all 4 steps of the financial assessment pipeline.

    Step 1 — Project Requirement
    Step 2 — Scheme Financing
    Step 3 — Repayment and Profitability
    Step 4 — Financial Feasibility

    financial_status values
    -----------------------
    "feasible"      — monthly_cash_flow > 0, no funding gap, financing confirmed.
    "modify"        — monthly_cash_flow > 0, but a funding gap exists OR financing
                      is not yet confirmed (no scheme supplied for a needed loan).
    "not_feasible"  — monthly_cash_flow <= 0 (business cannot service its costs).

    This is a financial feasibility assessment only.  It does NOT constitute
    credit approval or a guarantee of success.
    """

    # --- Step 1: Project Requirement ---
    business_name: str
    business_category: str
    location: str
    project_cost: float
    own_contribution: float
    own_contribution_surplus: float
    loan_required: float

    # --- Step 2: Scheme Financing ---
    funding_gap: float                         # loan_required − applicable_loan
    scheme_name: Optional[str]
    scheme_loan_cap: Optional[float]
    applicable_loan: float
    interest_rate: Optional[float]
    tenure_months: Optional[int]
    moratorium_months: int
    moratorium_repayment_note: str             # always set; explains future-work limitation

    # --- Step 3: Repayment ---
    monthly_emi: float
    total_repayment: float
    total_interest: float

    # --- Step 3: Profitability and Cash Flow ---
    monthly_revenue: float
    monthly_operating_cost: float
    monthly_fixed_cost: float
    monthly_total_cost: float
    monthly_cash_flow: float
    annual_cash_flow: float
    profit_margin_percentage: float
    operating_break_even_revenue: Optional[float]
    debt_service_break_even_revenue: Optional[float]
    estimated_payback_months: Optional[float]

    # --- Step 4: Feasibility ---
    financial_status: str   # "feasible" | "modify" | "not_feasible"
