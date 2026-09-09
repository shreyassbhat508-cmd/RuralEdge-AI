from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.benefit import BenefitResponse
from app.schemas.eligibility import EligibilityResponse
from app.schemas.scheme import SchemeResponse
from app.schemas.source import SourceResponse


class SchemeDetailsResponse(BaseModel):
    scheme: SchemeResponse
    eligibility: List[EligibilityResponse]
    benefits: List[BenefitResponse]
    source: Optional[SourceResponse] = None

    model_config = ConfigDict(from_attributes=True)
