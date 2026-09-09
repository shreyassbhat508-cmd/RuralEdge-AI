import logging
from fastapi import APIRouter, Response, status
from app.database import supabase
from app.schemas.health import HealthResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/health", tags=["Health"])


@router.get("", response_model=HealthResponse)
def health_check(response: Response):
    """
    GET /api/health
    Verifies FastAPI application status and performs a lightweight read-only check on Supabase connectivity.
    """
    db_status = "unavailable"
    try:
        res = supabase.table("schemes").select("id").limit(1).execute()
        if res.data is not None:
            db_status = "connected"
    except Exception as e:
        logger.error(f"Supabase health check failed: {str(e)}")
        db_status = "unavailable"

    if db_status == "connected":
        return HealthResponse(
            status="ok",
            service="RuralEdge Backend",
            database="connected",
        )
    else:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return HealthResponse(
            status="degraded",
            service="RuralEdge Backend",
            database="unavailable",
        )
