from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict


class LocationResponse(BaseModel):
    id: str
    state: Optional[str] = None
    district: Optional[str] = None
    taluk: Optional[str] = None
    village: Optional[str] = None
    pincode: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
