import logging
from typing import Any, Dict, List, Optional, cast
from app.database import supabase

logger = logging.getLogger(__name__)


def get_locations(
    state: Optional[str] = None,
    district: Optional[str] = None,
    taluk: Optional[str] = None,
    village: Optional[str] = None,
    pincode: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Retrieve locations from Supabase in a read-only manner based on optional filters.
    """
    try:
        builder = supabase.table("locations").select("*")

        if state and state.strip():
            s = state.strip().replace("%", "")
            if s:
                builder = builder.ilike("state", f"%{s}%")

        if district and district.strip():
            d = district.strip().replace("%", "")
            if d:
                builder = builder.ilike("district", f"%{d}%")

        if taluk and taluk.strip():
            t = taluk.strip().replace("%", "")
            if t:
                builder = builder.ilike("taluk", f"%{t}%")

        if village and village.strip():
            v = village.strip().replace("%", "")
            if v:
                builder = builder.ilike("village", f"%{v}%")

        if pincode and pincode.strip():
            p = pincode.strip().replace("%", "")
            if p:
                builder = builder.ilike("pincode", f"%{p}%")

        response = builder.execute()
        data = response.data
        if isinstance(data, list):
            return cast(List[Dict[str, Any]], data)
        return []
    except Exception as e:
        logger.error(f"Error fetching locations from Supabase: {str(e)}")
        raise RuntimeError("Failed to retrieve locations from database") from e
