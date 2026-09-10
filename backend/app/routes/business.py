"""Route handler for POST /api/business/analyze.

Follows the exact same pattern as the existing recommendation and loan
calculator routes: APIRouter + explicit HTTPException mapping.
"""

import logging
from fastapi import APIRouter, HTTPException, status
from app.schemas.business import BusinessAnalyzeRequest, BusinessAnalyzeResponse
from app.services.business_analysis_service import analyze_business

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/business", tags=["Business Analysis"])


@router.post(
    "/analyze",
    response_model=BusinessAnalyzeResponse,
    summary="Business Feasibility + Loan Intelligence Analysis",
    description=(
        "Accepts a business category, location, margin capital, and project cost. "
        "Returns a comprehensive analysis comprising finance metrics (EMI, loan amount, "
        "interest), scheme recommendation, opportunity scoring, SWOT analysis, and a "
        "market status section. Market competitor data is pending for phase 1 and is "
        "clearly labelled as such."
    ),
    responses={
        400: {"description": "Invalid input values (e.g. margin > project cost)"},
        422: {"description": "Request body validation error"},
        500: {"description": "Internal analysis error"},
    },
)
def analyze_business_endpoint(request: BusinessAnalyzeRequest) -> BusinessAnalyzeResponse:
    """
    POST /api/business/analyze

    Orchestrates:
    1. Finance engine  — EMI, loan amount, total interest (finance/ package)
    2. Scheme matcher  — deterministic scheme recommendation (recommendation_service)
    3. Opportunity     — scored from equity ratio + scheme match signal
    4. SWOT            — derived deterministically from inputs
    5. Market          — pending (no competitor DB in phase 1)
    """
    try:
        result = analyze_business(request)
        return result

    except ValueError as ve:
        logger.warning(
            "Validation error in POST /api/business/analyze: %s", str(ve)
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve),
        )

    except RuntimeError as re:
        logger.error(
            "Runtime error in POST /api/business/analyze: %s", str(re)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Business analysis failed due to an internal error. Please retry.",
        )

    except Exception as exc:
        logger.error(
            "Unexpected error in POST /api/business/analyze: %s (%s)",
            str(exc),
            type(exc).__name__,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred.",
        )
