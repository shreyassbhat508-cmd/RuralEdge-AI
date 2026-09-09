import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from app.schemas.source import SourceResponse
from app.services.source_service import get_sources

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/sources", tags=["Government Sources"])


@router.get("", response_model=List[SourceResponse])
def read_sources(
    source_type: Optional[str] = Query(None, description="Filter by source type (e.g. portal)"),
    organization: Optional[str] = Query(None, description="Filter by organization name"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
):
    """
    GET /api/sources
    Retrieve government sources with optional filters in a read-only manner.
    """
    try:
        sources = get_sources(
            source_type=source_type,
            organization=organization,
            is_active=is_active,
        )
        return sources
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to fetch government sources at this time.",
        )
    except Exception as e:
        logger.error(f"Unexpected error in GET /api/sources: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred.",
        )
