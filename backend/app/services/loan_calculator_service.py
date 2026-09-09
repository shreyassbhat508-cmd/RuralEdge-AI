from typing import List, Optional
from app.schemas.loan_calculator import (
    LoanCalculatorRequest,
    LoanCalculatorResponse,
    SchemeLoanCalculatorRequest,
    SchemeLoanCalculatorResponse,
)
from app.services.benefit_service import get_benefits_by_scheme_id
from app.services.scheme_service import get_scheme_by_id

DEFAULT_CALCULATION_NOTE = (
    "Estimated calculation for planning purposes. Actual loan terms, interest "
    "calculation, EMI, subsidy, moratorium and repayment schedule depend on the "
    "applicable government scheme and lending institution."
)

SCHEME_CALCULATION_NOTE = (
    "This is an estimate for planning purposes. Actual loan, subsidy, interest, EMI, "
    "eligibility, moratorium and repayment terms depend on the applicable government scheme "
    "and lending institution."
)


def calculate_loan(request: LoanCalculatorRequest) -> LoanCalculatorResponse:
    """
    Calculates simple loan financial metrics based on project cost, margin, interest rate,
    and repayment period in a purely deterministic calculation without database access.
    """
    if request.project_cost <= 0:
        raise ValueError("project_cost must be greater than 0")

    if request.margin_percentage < 0 or request.margin_percentage > 100:
        raise ValueError("margin_percentage must be between 0 and 100")

    if request.annual_interest_rate < 0:
        raise ValueError("annual_interest_rate must be greater than or equal to 0")

    if request.repayment_period_months <= 0:
        raise ValueError("repayment_period_months must be greater than 0")

    if request.moratorium_months < 0:
        raise ValueError("moratorium_months must be greater than or equal to 0")

    if request.moratorium_months > request.repayment_period_months:
        raise ValueError("moratorium_months must not be greater than repayment_period_months")

    margin_amount = round(request.project_cost * (request.margin_percentage / 100.0), 2)
    loan_amount = round(request.project_cost - margin_amount, 2)
    total_interest = round(
        loan_amount * (request.annual_interest_rate / 100.0) * (request.repayment_period_months / 12.0), 2
    )
    total_repayment = round(loan_amount + total_interest, 2)
    approx_monthly_payment = round(total_repayment / request.repayment_period_months, 2)

    return LoanCalculatorResponse(
        project_cost=request.project_cost,
        margin_percentage=request.margin_percentage,
        margin_amount=margin_amount,
        loan_amount=loan_amount,
        annual_interest_rate=request.annual_interest_rate,
        repayment_period_months=request.repayment_period_months,
        moratorium_months=request.moratorium_months,
        total_interest=total_interest,
        total_repayment=total_repayment,
        approx_monthly_payment=approx_monthly_payment,
        is_estimate=True,
        calculation_note=DEFAULT_CALCULATION_NOTE,
    )


def calculate_scheme_loan(
    scheme_id: str,
    request: SchemeLoanCalculatorRequest,
) -> SchemeLoanCalculatorResponse:
    """
    Calculates scheme loan financial structure using scheme benefit data retrieved from Supabase.
    """
    if request.project_cost <= 0:
        raise ValueError("project_cost must be greater than 0")

    if request.margin_percentage is not None:
        if request.margin_percentage < 0 or request.margin_percentage > 100:
            raise ValueError("margin_percentage must be between 0 and 100")

    scheme = get_scheme_by_id(scheme_id)
    if not scheme:
        raise KeyError("Scheme not found")

    benefits = get_benefits_by_scheme_id(scheme_id)
    if not benefits or len(benefits) == 0:
        raise ValueError("No benefit information available for this scheme")

    benefit = benefits[0]
    warnings: List[str] = []

    scheme_name = str(scheme.get("name") or scheme.get("short_name") or "Unnamed Scheme")

    interest_rate_raw = benefit.get("interest_rate")
    interest_rate = float(interest_rate_raw) if interest_rate_raw is not None else None

    repayment_period_raw = benefit.get("repayment_period_months")
    repayment_period_months = int(repayment_period_raw) if repayment_period_raw is not None else None

    moratorium_raw = benefit.get("moratorium_months")
    moratorium_months = int(moratorium_raw) if moratorium_raw is not None else None

    max_amount_raw = benefit.get("maximum_amount")
    maximum_amount = float(max_amount_raw) if max_amount_raw is not None else None

    subsidy_pct_raw = benefit.get("subsidy_percentage")
    subsidy_percentage = float(subsidy_pct_raw) if subsidy_pct_raw is not None else None

    # Maximum amount check
    if maximum_amount is not None and request.project_cost > maximum_amount:
        warnings.append("Project cost exceeds the scheme's maximum eligible amount.")

    # Subsidy calculation
    subsidy_amount: Optional[float] = None
    if subsidy_percentage is not None:
        subsidy_amount = round(request.project_cost * (subsidy_percentage / 100.0), 2)
    else:
        warnings.append("Subsidy information is not available for this scheme.")

    # Margin money calculation
    margin_percentage = request.margin_percentage
    margin_amount: Optional[float] = None
    if margin_percentage is not None:
        margin_amount = round(request.project_cost * (margin_percentage / 100.0), 2)
        loan_amount = round(request.project_cost - margin_amount, 2)
    else:
        loan_amount = request.project_cost
        warnings.append("No margin percentage was provided; no margin deduction was applied.")

    # Interest availability checks
    if interest_rate is None:
        warnings.append("Interest rate information is not available for this scheme.")

    if repayment_period_months is None:
        warnings.append("Repayment period information is not available for this scheme.")

    # Interest calculation
    total_interest: Optional[float] = None
    total_repayment: Optional[float] = None
    approx_monthly_payment: Optional[float] = None

    if interest_rate is not None and repayment_period_months is not None:
        total_interest = round(
            loan_amount * (interest_rate / 100.0) * (repayment_period_months / 12.0), 2
        )
        total_repayment = round(loan_amount + total_interest, 2)
        approx_monthly_payment = round(total_repayment / repayment_period_months, 2)

    return SchemeLoanCalculatorResponse(
        scheme_id=str(scheme_id),
        scheme_name=scheme_name,
        project_cost=request.project_cost,
        margin_percentage=margin_percentage,
        margin_amount=margin_amount,
        subsidy_percentage=subsidy_percentage,
        subsidy_amount=subsidy_amount,
        maximum_amount=maximum_amount,
        interest_rate=interest_rate,
        loan_amount=loan_amount,
        repayment_period_months=repayment_period_months,
        moratorium_months=moratorium_months,
        total_interest=total_interest,
        total_repayment=total_repayment,
        approx_monthly_payment=approx_monthly_payment,
        warnings=warnings,
        is_estimate=True,
        calculation_note=SCHEME_CALCULATION_NOTE,
    )
