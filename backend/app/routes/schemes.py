import logging
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Query, status
from app.schemas.benefit import BenefitResponse
from app.schemas.eligibility import EligibilityResponse
from app.schemas.scheme import PaginatedSchemeResponse, SchemeResponse
from app.schemas.scheme_details import SchemeDetailsResponse
from app.services.benefit_service import get_benefits_by_scheme_id
from app.services.eligibility_service import get_eligibility_by_scheme_id
from app.services.scheme_details_service import get_scheme_details_by_id
from app.services.scheme_service import (
    get_all_schemes,
    get_scheme_by_id,
    search_schemes,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/schemes", tags=["Schemes"])



@router.get("/search", response_model=List[SchemeResponse])
def search_schemes_endpoint(
    query: Optional[str] = Query(None, max_length=200, description="Search query string for name, short name, description, etc."),
    state: Optional[str] = Query(None, max_length=100, description="Filter by state"),
    scheme_type: Optional[str] = Query(None, max_length=100, description="Filter by scheme type (e.g. Central, State)"),
    status_filter: Optional[str] = Query(None, alias="status", max_length=50, description="Filter by status (e.g. active)"),
    ministry: Optional[str] = Query(None, max_length=150, description="Filter by ministry"),
):
    """
    GET /api/schemes/search
    Search schemes using optional query parameters in a read-only manner.
    """
    try:
        schemes = search_schemes(
            query=query,
            state=state,
            scheme_type=scheme_type,
            status=status_filter,
            ministry=ministry,
        )
        return schemes
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to search schemes at this time.",
        )
    except Exception as e:
        logger.error(f"Unexpected error in GET /api/schemes/search: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred.",
        )


@router.get("/{scheme_id}/eligibility", response_model=List[EligibilityResponse])
def read_scheme_eligibility(scheme_id: UUID):
    """
    GET /api/schemes/{scheme_id}/eligibility
    Retrieves eligibility criteria records for a scheme by scheme_id in a read-only manner.
    """
    try:
        eligibility_records = get_eligibility_by_scheme_id(str(scheme_id))
        return eligibility_records
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to fetch scheme eligibility at this time.",
        )
    except Exception as e:
        logger.error(f"Unexpected error in GET /api/schemes/{scheme_id}/eligibility: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred.",
        )


@router.get("/{scheme_id}/benefits", response_model=List[BenefitResponse])
def read_scheme_benefits(scheme_id: UUID):
    """
    GET /api/schemes/{scheme_id}/benefits
    Retrieves benefit records for a scheme by scheme_id in a read-only manner.
    """
    try:
        benefit_records = get_benefits_by_scheme_id(str(scheme_id))
        return benefit_records
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to fetch scheme benefits at this time.",
        )
    except Exception as e:
        logger.error(f"Unexpected error in GET /api/schemes/{scheme_id}/benefits: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred.",
        )


@router.get("/{scheme_id}/details", response_model=SchemeDetailsResponse)
def read_scheme_details(scheme_id: UUID):
    """
    GET /api/schemes/{scheme_id}/details
    Retrieves complete scheme details (scheme, eligibility, benefits, source) by scheme_id in a read-only manner.
    """
    try:
        details = get_scheme_details_by_id(str(scheme_id))
        if not details:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scheme not found",
            )
        return details
    except HTTPException:
        raise
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to fetch scheme details at this time.",
        )
    except Exception as e:
        logger.error(f"Unexpected error in GET /api/schemes/{scheme_id}/details: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred.",
        )



@router.get("/{scheme_id}", response_model=SchemeResponse)
def read_scheme_by_id(scheme_id: UUID):
    """
    GET /api/schemes/{scheme_id}
    Retrieves a single scheme by its UUID in a read-only manner.
    """
    try:
        scheme = get_scheme_by_id(str(scheme_id))
        if not scheme:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scheme not found",
            )
        return scheme
    except HTTPException:
        raise
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to fetch scheme at this time.",
        )
    except Exception as e:
        logger.error(f"Unexpected error in GET /api/schemes/{scheme_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred.",
        )


ALLOWED_SORT_BY = {"name", "launch_date", "created_at"}
ALLOWED_SORT_ORDER = {"asc", "desc"}


@router.get("", response_model=PaginatedSchemeResponse)
def read_schemes(
    state: Optional[str] = Query(None, max_length=100, description="Filter by supported state"),
    ministry: Optional[str] = Query(None, max_length=150, description="Filter by ministry name"),
    department: Optional[str] = Query(None, max_length=150, description="Filter by department name"),
    scheme_type: Optional[str] = Query(None, max_length=100, description="Filter by scheme type (e.g. Central, State)"),
    status_filter: Optional[str] = Query(None, alias="status", max_length=50, description="Filter by status (e.g. active)"),
    sort_by: str = Query("name", max_length=50, description="Field to sort by: name, launch_date, created_at"),
    sort_order: str = Query("asc", max_length=10, description="Sort order: asc, desc"),
    page: int = Query(1, description="Page number (>= 1)"),
    limit: int = Query(10, description="Items per page (1 to 100)"),
):
    """
    GET /api/schemes
    Retrieves schemes with optional filtering, sorting, and pagination in a read-only manner.
    """
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page parameter must be greater than or equal to 1.",
        )

    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit parameter must be between 1 and 100.",
        )

    sb = sort_by.strip()
    so = sort_order.strip().lower()

    if sb not in ALLOWED_SORT_BY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid sort_by field '{sort_by}'. Allowed values: {sorted(list(ALLOWED_SORT_BY))}",
        )

    if so not in ALLOWED_SORT_ORDER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid sort_order '{sort_order}'. Allowed values: 'asc', 'desc'",
        )

    try:
        paginated_result = get_all_schemes(
            state=state,
            ministry=ministry,
            department=department,
            scheme_type=scheme_type,
            status=status_filter,
            sort_by=sb,
            sort_order=so,
            page=page,
            limit=limit,
        )
        return paginated_result
    except HTTPException:
        raise
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to fetch schemes at this time.",
        )
    except Exception as e:
        logger.error(f"Unexpected error in GET /api/schemes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred.",
        )






