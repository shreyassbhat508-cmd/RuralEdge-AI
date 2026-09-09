import logging
from typing import Any, Dict, List, cast
from app.database import supabase

logger = logging.getLogger(__name__)


def get_eligibility_by_scheme_id(scheme_id: str) -> List[Dict[str, Any]]:
    """
    Retrieve eligibility requirements for a scheme from Supabase in a read-only manner.
    """
    try:
        response = (
            supabase.table("scheme_eligibility")
            .select("*")
            .eq("scheme_id", str(scheme_id))
            .execute()
        )
        data = response.data
        if isinstance(data, list):
            return cast(List[Dict[str, Any]], data)
        return []
    except Exception as e:
        logger.error(f"Error fetching eligibility for scheme_id '{scheme_id}' from Supabase: {str(e)}")
        raise RuntimeError("Failed to retrieve eligibility from database") from e
