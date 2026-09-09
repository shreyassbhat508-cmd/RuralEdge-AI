from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class LoanCalculatorRequest(BaseModel):
    project_cost: float = Field(..., gt=0, le=100000000, description="Total project cost (must be > 0 and <= 100,000,000)")
    margin_percentage: float = Field(..., ge=0, le=100, description="Beneficiary margin contribution percentage (0 to 100)")
    annual_interest_rate: float = Field(..., ge=0, le=100, description="Annual interest rate percentage (0 to 100)")
    repayment_period_months: int = Field(..., gt=0, le=600, description="Repayment period in months (1 to 600)")
    moratorium_months: int = Field(..., ge=0, description="Moratorium period in months (>= 0, <= repayment_period_months)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "project_cost": 1000000,
                "margin_percentage": 10,
                "annual_interest_rate": 6,
                "repayment_period_months": 60,
                "moratorium_months": 6,
            }
        }
    )


class LoanCalculatorResponse(BaseModel):
    project_cost: float
    margin_percentage: float
    margin_amount: float
    loan_amount: float
    annual_interest_rate: float
    repayment_period_months: int
    moratorium_months: int
    total_interest: float
    total_repayment: float
    approx_monthly_payment: float
    is_estimate: bool = True
    calculation_note: str = (
        "Estimated calculation for planning purposes. Actual loan terms, interest "
        "calculation, EMI, subsidy, moratorium and repayment schedule depend on the "
        "applicable government scheme and lending institution."
    )

    model_config = ConfigDict(from_attributes=True)


class SchemeLoanCalculatorRequest(BaseModel):
    project_cost: float = Field(..., gt=0, le=100000000, description="Total project cost (must be > 0 and <= 100,000,000)")
    margin_percentage: Optional[float] = Field(None, ge=0, le=100, description="Optional beneficiary margin contribution percentage (0 to 100)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "project_cost": 1000000,
                "margin_percentage": 10,
            }
        }
    )


class SchemeLoanCalculatorResponse(BaseModel):
    scheme_id: str
    scheme_name: str
    project_cost: float
    margin_percentage: Optional[float] = None
    margin_amount: Optional[float] = None
    subsidy_percentage: Optional[float] = None
    subsidy_amount: Optional[float] = None
    maximum_amount: Optional[float] = None
    interest_rate: Optional[float] = None
    loan_amount: float
    repayment_period_months: Optional[int] = None
    moratorium_months: Optional[int] = None
    total_interest: Optional[float] = None
    total_repayment: Optional[float] = None
    approx_monthly_payment: Optional[float] = None
    warnings: List[str] = Field(default_factory=list)
    is_estimate: bool = True
    calculation_note: str = (
        "This is an estimate for planning purposes. Actual loan, subsidy, interest, EMI, "
        "eligibility, moratorium and repayment terms depend on the applicable government scheme "
        "and lending institution."
    )

    model_config = ConfigDict(from_attributes=True)
