from typing import List
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.scheme import SchemeResponse


class EligibilityCheckResponse(BaseModel):
    scheme: SchemeResponse
    eligible: bool
    reasons: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
