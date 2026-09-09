from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict


class IngestionRunResponse(BaseModel):
    id: str
    source_id: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    status: Optional[str] = None
    documents_found: Optional[int] = None
    documents_processed: Optional[int] = None
    documents_failed: Optional[int] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)
