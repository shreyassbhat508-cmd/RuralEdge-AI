import logging
from typing import List
from fastapi import APIRouter, HTTPException, status
from app.schemas.recommendation import RecommendationRequest, SchemeRecommendation
from app.services.recommendation_service import get_recommendations

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/recommendations", tags=["Recommendations"])


@router.post("", response_model=List[SchemeRecommendation])
def create_recommendations(request: RecommendationRequest):
    """
    POST /api/recommendations
    Accepts user eligibility details and returns matching schemes in a read-only manner using deterministic rules (No AI).
    """
    try:
        recommendations = get_recommendations(request)
        return recommendations
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to compute recommendations at this time.",
        )
    except Exception as e:
        logger.error(f"Unexpected error in POST /api/recommendations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred.",
        )
