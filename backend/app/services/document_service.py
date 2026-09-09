import logging
from typing import Any, Dict, List, Optional, Union, cast
from uuid import UUID
from app.database import supabase

logger = logging.getLogger(__name__)


def get_documents(
    source_id: Optional[Union[UUID, str]] = None,
    document_type: Optional[str] = None,
    language: Optional[str] = None,
    processing_status: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Retrieve raw documents from Supabase in a read-only manner based on optional filters.
    """
    try:
        builder = supabase.table("raw_documents").select("*")

        if source_id:
            builder = builder.eq("source_id", str(source_id))

        if document_type and document_type.strip():
            dt = document_type.strip().replace("%", "")
            if dt:
                builder = builder.ilike("document_type", f"%{dt}%")

        if language and language.strip():
            lang = language.strip().replace("%", "")
            if lang:
                builder = builder.ilike("language", f"%{lang}%")

        if processing_status and processing_status.strip():
            ps = processing_status.strip().replace("%", "")
            if ps:
                builder = builder.ilike("processing_status", f"%{ps}%")

        response = builder.execute()
        data = response.data
        if isinstance(data, list):
            return cast(List[Dict[str, Any]], data)
        return []
    except Exception as e:
        logger.error(f"Error fetching raw documents from Supabase: {str(e)}")
        raise RuntimeError("Failed to retrieve raw documents from database") from e
