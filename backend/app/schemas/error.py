from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ErrorDetail(BaseModel):
    code: str = Field(..., description="Error code identifier")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[List[Dict[str, Any]]] = Field(None, description="Optional field-level validation details")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": "SCHEME_NOT_FOUND",
                "message": "Scheme not found",
            }
        }
    )


class ErrorResponse(BaseModel):
    success: bool = Field(False, description="Always false for error responses")
    error: ErrorDetail

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": False,
                "error": {
                    "code": "SCHEME_NOT_FOUND",
                    "message": "Scheme not found",
                },
            }
        }
    )
