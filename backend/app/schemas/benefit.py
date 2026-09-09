from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict


class BenefitResponse(BaseModel):
    id: str
    scheme_id: str
    benefit_type: Optional[str] = None
    amount: Optional[float] = None
    interest_rate: Optional[float] = None
    subsidy_percentage: Optional[float] = None
    maximum_amount: Optional[float] = None
    repayment_period_months: Optional[int] = None
    moratorium_months: Optional[int] = None
    description: Optional[str] = None
    benefit_data: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
