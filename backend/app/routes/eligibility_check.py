import logging
from uuid import UUID
from fastapi import APIRouter, HTTPException, status
from app.schemas.eligibility_check import EligibilityCheckResponse
from app.schemas.recommendation import RecommendationRequest
from app.services.eligibility_check_service import check_scheme_eligibility

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/schemes", tags=["Eligibility Check"])


@router.post("/{scheme_id}/eligibility-check", response_model=EligibilityCheckResponse)
def check_eligibility_endpoint(scheme_id: UUID, request: RecommendationRequest):
    """
    POST /api/schemes/{scheme_id}/eligibility-check
    Checks user eligibility against a single specific scheme in a read-only manner.
    """
    try:
        response = check_scheme_eligibility(str(scheme_id), request)
        return response
    except KeyError as ke:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(ke).strip("'\""),
        )
    except HTTPException:
        raise
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to perform eligibility check at this time.",
        )
    except Exception as e:
        logger.error(f"Unexpected error in POST /api/schemes/{scheme_id}/eligibility-check: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred.",
        )
