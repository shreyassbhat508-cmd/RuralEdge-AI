from typing import Optional
from pydantic import BaseModel, ConfigDict


class SourceResponse(BaseModel):
    id: str
    name: str
    organization: Optional[str] = None
    source_type: Optional[str] = None
    base_url: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
