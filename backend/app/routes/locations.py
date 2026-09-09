import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from app.schemas.location import LocationResponse
from app.services.location_service import get_locations

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/locations", tags=["Locations"])


@router.get("", response_model=List[LocationResponse])
def read_locations(
    state: Optional[str] = Query(None, description="Filter by state name"),
    district: Optional[str] = Query(None, description="Filter by district name"),
    taluk: Optional[str] = Query(None, description="Filter by taluk name"),
    village: Optional[str] = Query(None, description="Filter by village name"),
    pincode: Optional[str] = Query(None, description="Filter by pincode"),
):
    """
    GET /api/locations
    Retrieve locations with optional filters in a read-only manner.
    """
    try:
        locations = get_locations(
            state=state,
            district=district,
            taluk=taluk,
            village=village,
            pincode=pincode,
        )
        return locations
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to fetch locations at this time.",
        )
    except Exception as e:
        logger.error(f"Unexpected error in GET /api/locations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred.",
        )
