import logging
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Query, status
from app.schemas.ingestion import IngestionRunResponse
from app.services.ingestion_service import get_ingestion_runs

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ingestion", tags=["Ingestion"])


@router.get("", response_model=List[IngestionRunResponse])
def read_ingestion_runs(
    source_id: Optional[UUID] = Query(None, description="Filter by government source UUID"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (e.g. completed, failed)"),
):
    """
    GET /api/ingestion
    Retrieve ingestion runs with optional filters in a read-only manner.
    """
    try:
        runs = get_ingestion_runs(
            source_id=source_id,
            status=status_filter,
        )
        return runs
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to fetch ingestion runs at this time.",
        )
    except Exception as e:
        logger.error(f"Unexpected error in GET /api/ingestion: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred.",
        )
