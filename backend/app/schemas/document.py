from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict


class RawDocumentResponse(BaseModel):
    id: str
    source_id: Optional[str] = None
    title: Optional[str] = None
    document_url: Optional[str] = None
    document_type: Optional[str] = None
    raw_content: Optional[str] = None
    content_hash: Optional[str] = None
    language: Optional[str] = None
    published_at: Optional[str] = None
    fetched_at: Optional[str] = None
    processing_status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
