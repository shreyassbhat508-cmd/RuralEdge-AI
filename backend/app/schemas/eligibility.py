from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict


class EligibilityResponse(BaseModel):
    id: str
    scheme_id: str
    category: Optional[str] = None
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    gender: Optional[str] = None
    occupation: Optional[str] = None
    income_min: Optional[float] = None
    income_max: Optional[float] = None
    education: Optional[str] = None
    location_requirement: Optional[str] = None
    caste_category: Optional[str] = None
    disability_required: Optional[bool] = None
    land_required: Optional[bool] = None
    business_required: Optional[bool] = None
    other_conditions: Optional[str] = None
    eligibility_data: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
