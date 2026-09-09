from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.recommendation import RecommendationRequest


class AIChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User question or prompt for the AI assistant (max 2000 characters)",
    )
    scheme_id: Optional[str] = Field(
        None, description="Optional scheme UUID to provide scheme-specific context"
    )
    user_context: Optional[RecommendationRequest] = Field(
        None, description="Optional user demographic and eligibility profile"
    )
    language: Optional[str] = Field(
        None,
        max_length=50,
        description="Optional preferred language for response (e.g. English, Hindi, Kannada)",
    )

    model_config = ConfigDict(from_attributes=True)


class AIChatResponse(BaseModel):
    reply: str = Field(..., description="AI assistant reply in simple, clear language")
    scheme_id: Optional[str] = Field(None, description="Associated scheme UUID if applicable")
    sources: List[str] = Field(
        default_factory=list, description="Official source URLs or references if available"
    )
    disclaimer: str = Field(
        "This AI assistant provides informational guidance based on stored government scheme records. It does not determine official eligibility or process government applications. Please verify details with official government portals.",
        description="Standard disclaimer",
    )

    model_config = ConfigDict(from_attributes=True)
