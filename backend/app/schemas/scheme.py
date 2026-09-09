from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict


class SchemeResponse(BaseModel):
    id: str
    source_id: Optional[str] = None
    name: str
    short_name: Optional[str] = None
    ministry: Optional[str] = None
    department: Optional[str] = None
    description: Optional[str] = None
    scheme_type: Optional[str] = None
    official_url: Optional[str] = None
    application_url: Optional[str] = None
    launch_date: Optional[str] = None
    status: Optional[str] = None
    target_beneficiaries: Optional[Any] = None
    states: Optional[Any] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PaginatedSchemeResponse(BaseModel):
    items: List[SchemeResponse]
    page: int
    limit: int
    total: int
    total_pages: int

    model_config = ConfigDict(from_attributes=True)
