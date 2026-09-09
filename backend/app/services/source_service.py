import logging
from typing import Any, Dict, List, Optional, cast
from app.database import supabase

logger = logging.getLogger(__name__)


def get_sources(
    source_type: Optional[str] = None,
    organization: Optional[str] = None,
    is_active: Optional[bool] = None,
) -> List[Dict[str, Any]]:
    """
    Retrieve government sources from Supabase in a read-only manner based on optional filters.
    """
    try:
        builder = supabase.table("government_sources").select("*")

        if source_type and source_type.strip():
            st = source_type.strip().replace("%", "")
            if st:
                builder = builder.ilike("source_type", f"%{st}%")

        if organization and organization.strip():
            org = organization.strip().replace("%", "")
            if org:
                builder = builder.ilike("organization", f"%{org}%")

        if is_active is not None:
            builder = builder.eq("is_active", is_active)

        response = builder.execute()
        data = response.data
        if isinstance(data, list):
            return cast(List[Dict[str, Any]], data)
        return []
    except Exception as e:
        logger.error(f"Error fetching government sources from Supabase: {str(e)}")
        raise RuntimeError("Failed to retrieve government sources from database") from e
