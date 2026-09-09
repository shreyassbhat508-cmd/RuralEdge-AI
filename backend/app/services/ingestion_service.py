import logging
from typing import Any, Dict, List, Optional, Union, cast
from uuid import UUID
from app.database import supabase

logger = logging.getLogger(__name__)


def get_ingestion_runs(
    source_id: Optional[Union[UUID, str]] = None,
    status: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Retrieve ingestion runs from Supabase in a read-only manner based on optional filters.
    """
    try:
        builder = supabase.table("ingestion_runs").select("*")

        if source_id:
            builder = builder.eq("source_id", str(source_id))

        if status and status.strip():
            stat = status.strip().replace("%", "")
            if stat:
                builder = builder.ilike("status", f"%{stat}%")

        response = builder.execute()
        data = response.data
        if isinstance(data, list):
            return cast(List[Dict[str, Any]], data)
        return []
    except Exception as e:
        logger.error(f"Error fetching ingestion runs from Supabase: {str(e)}")
        raise RuntimeError("Failed to retrieve ingestion runs from database") from e
