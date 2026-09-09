import logging
from typing import Any, Dict, List, cast
from app.database import supabase

logger = logging.getLogger(__name__)


def get_benefits_by_scheme_id(scheme_id: str) -> List[Dict[str, Any]]:
    """
    Retrieve scheme benefits from Supabase in a read-only manner.
    """
    try:
        response = (
            supabase.table("scheme_benefits")
            .select("*")
            .eq("scheme_id", str(scheme_id))
            .execute()
        )
        data = response.data
        if isinstance(data, list):
            return cast(List[Dict[str, Any]], data)
        return []
    except Exception as e:
        logger.error(f"Error fetching benefits for scheme_id '{scheme_id}' from Supabase: {str(e)}")
        raise RuntimeError("Failed to retrieve benefits from database") from e
