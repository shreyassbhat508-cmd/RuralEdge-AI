import math
import logging
from typing import Any, Dict, List, Optional, cast
from postgrest.types import CountMethod
from app.database import supabase

logger = logging.getLogger(__name__)


def get_all_schemes(
    state: Optional[str] = None,
    ministry: Optional[str] = None,
    department: Optional[str] = None,
    scheme_type: Optional[str] = None,
    status: Optional[str] = None,
    sort_by: str = "name",
    sort_order: str = "asc",
    page: int = 1,
    limit: int = 10,
) -> Dict[str, Any]:
    """
    Retrieve schemes from Supabase in a read-only manner with optional filtering, sorting, and pagination.
    """
    try:
        builder = supabase.table("schemes").select("*", count=CountMethod.exact)

        if state and state.strip():
            s = state.strip()
            builder = builder.cs("states", [s])

        if ministry and ministry.strip():
            m = ministry.strip().replace("%", "")
            if m:
                builder = builder.ilike("ministry", f"%{m}%")

        if department and department.strip():
            d = department.strip().replace("%", "")
            if d:
                builder = builder.ilike("department", f"%{d}%")

        if scheme_type and scheme_type.strip():
            st = scheme_type.strip().replace("%", "")
            if st:
                builder = builder.ilike("scheme_type", f"%{st}%")

        if status and status.strip():
            stat = status.strip().replace("%", "")
            if stat:
                builder = builder.ilike("status", f"%{stat}%")

        desc_flag = True if sort_order.lower() == "desc" else False
        builder = builder.order(sort_by, desc=desc_flag)

        offset_start = (page - 1) * limit
        offset_end = offset_start + limit - 1

        builder = builder.range(offset_start, offset_end)

        response = builder.execute()
        raw_data = response.data
        data = cast(List[Dict[str, Any]], raw_data) if isinstance(raw_data, list) else []

        total = response.count if response.count is not None else len(data)
        total_pages = math.ceil(total / limit) if total > 0 else 0

        return {
            "items": data,
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": total_pages,
        }
    except Exception as e:
        logger.error(f"Error fetching schemes from Supabase: {str(e)}")
        raise RuntimeError("Failed to retrieve schemes from database") from e




def search_schemes(
    query: Optional[str] = None,
    state: Optional[str] = None,
    scheme_type: Optional[str] = None,
    status: Optional[str] = None,
    ministry: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Search schemes from Supabase in a read-only manner based on optional filters.
    """
    try:
        builder = supabase.table("schemes").select("*")

        if query and query.strip():
            q = query.strip().replace(",", " ").replace("%", "")
            if q:
                builder = builder.or_(
                    f"name.ilike.%{q}%,short_name.ilike.%{q}%,description.ilike.%{q}%,ministry.ilike.%{q}%,department.ilike.%{q}%"
                )

        if state and state.strip():
            s = state.strip().replace("%", "")
            if s:
                builder = builder.ilike("states", f"%{s}%")

        if scheme_type and scheme_type.strip():
            st = scheme_type.strip().replace("%", "")
            if st:
                builder = builder.ilike("scheme_type", f"%{st}%")

        if status and status.strip():
            stat = status.strip().replace("%", "")
            if stat:
                builder = builder.ilike("status", f"%{stat}%")

        if ministry and ministry.strip():
            m = ministry.strip().replace("%", "")
            if m:
                builder = builder.ilike("ministry", f"%{m}%")

        response = builder.execute()
        data = response.data
        if isinstance(data, list):
            return cast(List[Dict[str, Any]], data)
        return []
    except Exception as e:
        logger.error(f"Error searching schemes from Supabase: {str(e)}")
        raise RuntimeError("Failed to search schemes from database") from e


def get_scheme_by_id(scheme_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a single scheme from Supabase by its ID in a read-only manner.
    """
    try:
        response = (
            supabase.table("schemes")
            .select("*")
            .eq("id", str(scheme_id))
            .execute()
        )
        data = response.data
        if isinstance(data, list) and len(data) > 0:
            return cast(Dict[str, Any], data[0])
        return None
    except Exception as e:
        logger.error(f"Error fetching scheme by id '{scheme_id}' from Supabase: {str(e)}")
        raise RuntimeError("Failed to retrieve scheme from database") from e




