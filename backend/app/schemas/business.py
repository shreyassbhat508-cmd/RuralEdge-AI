"""Pydantic schemas for POST /api/business/analyze endpoint.

Follows the conventions established in the existing schema modules:
  - BaseModel + Field for validation
  - ConfigDict(from_attributes=True) on response models
  - Optional types with None defaults for pending/unavailable data
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Request
# ---------------------------------------------------------------------------

class LocationInput(BaseModel):
    """Geographic location for the business analysis."""

    state: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="State name (e.g. 'Karnataka')",
    )
    district: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="District name (e.g. 'Kodagu')",
    )
    village: Optional[str] = Field(
        None,
        max_length=200,
        description="Village or town name (optional)",
    )

    model_config = ConfigDict(from_attributes=True)


class BusinessAnalyzeRequest(BaseModel):
    """Request body for POST /api/business/analyze."""

    location: LocationInput = Field(..., description="Geographic location of the business")
    business_category: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Business category (e.g. 'Dairy', 'Poultry', 'Agri-tech')",
    )
    margin_capital: float = Field(
        ...,
        ge=0,
        le=100_000_000,
        description="Applicant's own capital contribution in INR (≥ 0)",
    )
    project_cost: float = Field(
        ...,
        gt=0,
        le=100_000_000,
        description="Total project cost in INR (> 0)",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "location": {
                    "state": "Karnataka",
                    "district": "Kodagu",
                    "village": "Madikeri",
                },
                "business_category": "Dairy",
                "margin_capital": 100000,
                "project_cost": 1000000,
            }
        }
    )


# ---------------------------------------------------------------------------
# Response sub-models
# ---------------------------------------------------------------------------

class BusinessInfo(BaseModel):
    """Core business identification in the response."""

    category: str
    location: Dict[str, Optional[str]]

    model_config = ConfigDict(from_attributes=True)


class CompetitorDetail(BaseModel):
    """Details of an individual competing business from Places API."""

    name: str = Field(..., description="Business name")
    address: Optional[str] = Field(None, description="Physical address or location")
    category: Optional[str] = Field(None, description="Business category/type")
    distance_km: Optional[float] = Field(None, description="Distance from target location in km")
    rating: Optional[float] = Field(None, description="Average rating (0.0 - 5.0)")
    user_ratings_total: Optional[int] = Field(None, description="Total user ratings count")

    model_config = ConfigDict(from_attributes=True)


class MarketInfo(BaseModel):
    """Market / competitor intelligence section powered by Google Places API."""

    source: str = Field(
        default="fallback_unavailable",
        description="Data provider ('google_places' | 'fallback_unavailable')",
    )
    status: str = Field(
        default="pending",
        description="'success' | 'no_results' | 'pending' | 'unavailable' | 'error'",
    )
    radius_km: int = Field(default=10, ge=0)
    competitor_count: int = Field(default=0, ge=0)
    competitors: List[CompetitorDetail] = Field(default_factory=list)
    market_reach_score: int = Field(default=0, ge=0, le=100)
    competition_score: int = Field(default=70, ge=0, le=100, description="Competitor density feasibility score (0-100)")

    model_config = ConfigDict(from_attributes=True)


class OpportunityComponents(BaseModel):
    """Component scores for the weighted business feasibility model."""

    market: int = Field(default=0, ge=0, le=100, description="Market potential score (25% weight)")
    competition: int = Field(default=0, ge=0, le=100, description="Competition score (20% weight)")
    financial: int = Field(default=0, ge=0, le=100, description="Financial feasibility score (25% weight)")
    location: int = Field(default=0, ge=0, le=100, description="Location/accessibility score (10% weight)")
    affordability: int = Field(default=0, ge=0, le=100, description="Affordability score (20% weight)")

    model_config = ConfigDict(from_attributes=True)


class OpportunityInfo(BaseModel):
    """Opportunity score and component analysis."""

    score: int = Field(default=0, ge=0, le=100)
    level: str = Field(default="Pending")
    components: OpportunityComponents = Field(default_factory=OpportunityComponents)
    reasons: List[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class FinanceInfo(BaseModel):
    """Financial analysis section, powered by the finance/ engine.

    All monetary values are in INR, rounded to 2 decimal places.
    When the finance engine cannot compute a value it is 0 and
    'is_estimate' remains True.
    """

    project_cost: float
    own_contribution: float
    loan_amount: float
    monthly_revenue: float = 0.0
    monthly_operating_cost: float = 0.0
    monthly_profit: float = 0.0
    profit_margin: float = 0.0
    emi: float = 0.0
    total_interest: float = 0.0
    break_even: Optional[float] = None
    payback_months: Optional[float] = None
    is_estimate: bool = True
    calculation_note: str = (
        "Estimated calculation for planning purposes. Actual loan terms, interest "
        "calculation, EMI, subsidy, moratorium and repayment schedule depend on the "
        "applicable government scheme and lending institution."
    )

    model_config = ConfigDict(from_attributes=True)


class SchemeInfo(BaseModel):
    """Scheme recommendation section, powered by the recommendation service."""

    status: str = Field(
        default="pending",
        description="'matched' | 'no_match' | 'pending' | 'error'",
    )
    recommended_scheme: Optional[str] = None
    match_score: int = Field(default=0, ge=0, le=100)
    reasons: List[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class SwotAnalysis(BaseModel):
    """SWOT analysis for the business.

    Populated deterministically from the inputs.
    """

    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    opportunities: List[str] = Field(default_factory=list)
    threats: List[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Composite response
# ---------------------------------------------------------------------------

class BusinessAnalyzeResponse(BaseModel):
    """Full response for POST /api/business/analyze."""

    business: BusinessInfo
    market: MarketInfo
    opportunity: OpportunityInfo
    finance: FinanceInfo
    scheme: SchemeInfo
    swot: SwotAnalysis

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "business": {
                    "category": "Dairy",
                    "location": {
                        "state": "Karnataka",
                        "district": "Kodagu",
                        "village": "Madikeri",
                    },
                },
                "market": {
                    "status": "pending",
                    "competitor_count": 0,
                    "radius_km": 10,
                    "market_reach_score": 0,
                },
                "opportunity": {
                    "score": 0,
                    "level": "Pending",
                    "reasons": [],
                },
                "finance": {
                    "project_cost": 1000000,
                    "own_contribution": 100000,
                    "loan_amount": 900000,
                    "monthly_revenue": 0,
                    "monthly_operating_cost": 0,
                    "monthly_profit": 0,
                    "profit_margin": 0,
                    "emi": 0,
                    "total_interest": 0,
                    "break_even": None,
                    "payback_months": None,
                    "is_estimate": True,
                },
                "scheme": {
                    "status": "pending",
                    "recommended_scheme": None,
                    "match_score": 0,
                    "reasons": [],
                },
                "swot": {
                    "strengths": [],
                    "weaknesses": [],
                    "opportunities": [],
                    "threats": [],
                },
            }
        },
    )
