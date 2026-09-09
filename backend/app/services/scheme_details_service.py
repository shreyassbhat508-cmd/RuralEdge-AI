import logging
from typing import Any, Dict, List, Optional, cast
from app.database import supabase

logger = logging.getLogger(__name__)


def get_scheme_details_by_id(scheme_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve complete scheme details (scheme, eligibility, benefits, source) by scheme_id in a read-only manner.
    """
    try:
        # 1. Fetch scheme record
        scheme_res = (
            supabase.table("schemes")
            .select("*")
            .eq("id", str(scheme_id))
            .execute()
        )
        raw_schemes = scheme_res.data
        if not isinstance(raw_schemes, list) or len(raw_schemes) == 0:
            return None

        scheme = cast(Dict[str, Any], raw_schemes[0])

        # 2. Fetch eligibility records
        elig_res = (
            supabase.table("scheme_eligibility")
            .select("*")
            .eq("scheme_id", str(scheme_id))
            .execute()
        )
        raw_elig = elig_res.data
        eligibility = cast(List[Dict[str, Any]], raw_elig) if isinstance(raw_elig, list) else []

        # 3. Fetch benefit records
        ben_res = (
            supabase.table("scheme_benefits")
            .select("*")
            .eq("scheme_id", str(scheme_id))
            .execute()
        )
        raw_ben = ben_res.data
        benefits = cast(List[Dict[str, Any]], raw_ben) if isinstance(raw_ben, list) else []

        # 4. Fetch government source record if source_id exists
        source: Optional[Dict[str, Any]] = None
        source_id = scheme.get("source_id")
        if isinstance(source_id, str) and source_id.strip():
            src_res = (
                supabase.table("government_sources")
                .select("*")
                .eq("id", source_id.strip())
                .execute()
            )
            raw_src = src_res.data
            if isinstance(raw_src, list) and len(raw_src) > 0:
                source = cast(Dict[str, Any], raw_src[0])

        return {
            "scheme": scheme,
            "eligibility": eligibility,
            "benefits": benefits,
            "source": source,
        }

    except Exception as e:
        logger.error(f"Error fetching scheme details for scheme_id '{scheme_id}' from Supabase: {str(e)}")
        raise RuntimeError("Failed to retrieve scheme details from database") from e
