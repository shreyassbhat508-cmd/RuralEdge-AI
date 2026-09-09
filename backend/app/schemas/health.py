from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    status: str = Field(..., description="Overall health status (e.g. ok, degraded)")
    service: str = Field("RuralEdge Backend", description="Service name")
    database: str = Field(..., description="Database connection status (e.g. connected, unavailable)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "ok",
                "service": "RuralEdge Backend",
                "database": "connected",
            }
        }
    )
