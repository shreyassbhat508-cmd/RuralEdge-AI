from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class LocationInput(BaseModel):
    state: str = Field(..., min_length=1, max_length=100, description="State name (required)")
    district: str = Field(..., min_length=1, max_length=100, description="District name (required)")
    village: Optional[str] = Field(None, max_length=100, description="Optional village name")

    @field_validator("state", "district", mode="before")
    @classmethod
    def validate_non_empty_str(cls, v: Any) -> str:
        if not isinstance(v, str) or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only")
        return v.strip()


class BusinessAnalyzeRequest(BaseModel):
    location: LocationInput
    business_category: str = Field(..., min_length=1, max_length=100, description="Business category (required)")
    margin_capital: float = Field(..., ge=0, description="Beneficiary margin contribution (>= 0)")
    project_cost: float = Field(..., gt=0, le=100000000, description="Total project cost (> 0)")

    @field_validator("business_category", mode="before")
    @classmethod
    def validate_category(cls, v: Any) -> str:
        if not isinstance(v, str) or not v.strip():
            raise ValueError("business_category cannot be empty or whitespace only")
        return v.strip()

    @model_validator(mode="after")
    def validate_margin_vs_project(self) -> "BusinessAnalyzeRequest":
        if self.margin_capital > self.project_cost:
            raise ValueError("margin_capital must not exceed project_cost")
        return self

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "location": {
                    "state": "Karnataka",
                    "district": "Kodagu",
                    "village": "XYZ Village",
                },
                "business_category": "Dairy",
                "margin_capital": 100000,
                "project_cost": 1000000,
            }
        }
    )


class BusinessInfo(BaseModel):
    category: str
    location: Dict[str, Optional[str]]
    project_cost: float
    margin_capital: float


class MarketInfo(BaseModel):
    status: str = "insufficient_data"
    message: str = "Market intelligence data is not available yet."


class OpportunityInfo(BaseModel):
    status: str = "pending_market_analysis"
    score: Optional[float] = None
    message: str = "Opportunity score will be calculated when market intelligence is available."


class FinanceInfo(BaseModel):
    project_cost: float
    margin_contribution: float
    margin_percentage: float
    loan_amount: float
    approx_monthly_payment: Optional[float] = None
    total_interest: Optional[float] = None
    total_repayment: Optional[float] = None
    repayment_period_months: Optional[int] = None
    calculation_note: Optional[str] = None


class SchemeInfo(BaseModel):
    status: str
    recommended_scheme: Optional[Dict[str, Any]] = None


class SWOTInfo(BaseModel):
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    opportunities: List[str] = Field(default_factory=list)
    threats: List[str] = Field(default_factory=list)


class BusinessAnalyzeResponse(BaseModel):
    business: BusinessInfo
    market: MarketInfo
    opportunity: OpportunityInfo
    finance: FinanceInfo
    scheme: SchemeInfo
    swot: SWOTInfo

    model_config = ConfigDict(from_attributes=True)
