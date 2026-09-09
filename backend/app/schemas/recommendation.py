from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.benefit import BenefitResponse
from app.schemas.eligibility import EligibilityResponse
from app.schemas.scheme import SchemeResponse


class RecommendationRequest(BaseModel):
    state: Optional[str] = Field(None, max_length=100, description="State name (max 100 characters)")
    district: Optional[str] = Field(None, max_length=100, description="District name (max 100 characters)")
    age: Optional[int] = Field(None, ge=0, le=150, description="Age in years")
    gender: Optional[str] = Field(None, max_length=50, description="Gender (max 50 characters)")
    occupation: Optional[str] = Field(None, max_length=100, description="Occupation (max 100 characters)")
    annual_income: Optional[float] = Field(None, ge=0, description="Annual income")
    caste_category: Optional[str] = Field(None, max_length=100, description="Caste category (max 100 characters)")
    education: Optional[str] = Field(None, max_length=100, description="Education qualification (max 100 characters)")
    disability: Optional[bool] = Field(None, description="Disability status")
    land_owned: Optional[bool] = Field(None, description="Land ownership status")
    business_exists: Optional[bool] = Field(None, description="Existing business status")

    model_config = ConfigDict(from_attributes=True)


class SchemeRecommendation(BaseModel):
    scheme: SchemeResponse
    eligibility: List[EligibilityResponse]
    benefits: List[BenefitResponse]
    match_reasons: List[str] = Field(default_factory=list, description="List of transparent match reasons")
    match_score: int = Field(0, ge=0, le=100, description="Deterministic match score from 0 to 100")
    warnings: List[str] = Field(default_factory=list, description="Missing or unknown eligibility warnings")

    model_config = ConfigDict(from_attributes=True)
