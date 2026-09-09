import logging
import os
from typing import Any, Dict, List
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.routes.ai import router as ai_router
from app.routes.documents import router as documents_router
from app.routes.eligibility_check import router as eligibility_check_router
from app.routes.health import router as health_router
from app.routes.ingestion import router as ingestion_router
from app.routes.loan_calculator import router as loan_calculator_router
from app.routes.locations import router as locations_router
from app.routes.recommendations import router as recommendations_router
from app.routes.schemes import router as schemes_router
from app.routes.sources import router as sources_router
from app.schemas.error import ErrorResponse

logger = logging.getLogger(__name__)


def _get_error_code(status_code: int, detail: Any) -> str:
    detail_str = str(detail).lower() if detail else ""
    if status_code == 404:
        if "scheme" in detail_str:
            return "SCHEME_NOT_FOUND"
        if "benefit" in detail_str:
            return "BENEFITS_NOT_FOUND"
        return "NOT_FOUND"
    elif status_code == 400:
        if "page" in detail_str or "limit" in detail_str:
            return "INVALID_PAGINATION"
        if "sort" in detail_str:
            return "INVALID_SORT_PARAMETER"
        if any(term in detail_str for term in ["project_cost", "margin", "interest", "moratorium", "repayment"]):
            return "INVALID_CALCULATOR_INPUT"
        return "BAD_REQUEST"
    elif status_code == 413:
        return "PAYLOAD_TOO_LARGE"
    elif status_code == 422:
        return "VALIDATION_ERROR"
    elif status_code == 503:
        if any(term in detail_str for term in ["ai", "gemini", "assistant"]):
            return "AI_SERVICE_UNAVAILABLE"
        return "SERVICE_UNAVAILABLE"
    elif status_code == 500:
        return "INTERNAL_SERVER_ERROR"
    return "ERROR"


app = FastAPI(
    title="RuralEdge API",
    description="Backend API for RuralEdge",
    version="1.0.0",
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        404: {"model": ErrorResponse, "description": "Resource Not Found"},
        422: {"model": ErrorResponse, "description": "Validation Error"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)

allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "")
allowed_origins = [
    origin.strip()
    for origin in allowed_origins_env.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_BODY_SIZE = 1_048_576  # 1 MB limit for request bodies


@app.middleware("http")
async def limit_body_size_middleware(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > MAX_BODY_SIZE:
                return JSONResponse(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    content={
                        "success": False,
                        "error": {
                            "code": "PAYLOAD_TOO_LARGE",
                            "message": "Request payload too large",
                        },
                    },
                )
        except ValueError:
            pass
    return await call_next(request)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    code = _get_error_code(exc.status_code, exc.detail)
    message = str(exc.detail) if exc.detail else "An error occurred"
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": code,
                "message": message,
            },
        },
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    formatted_details: List[Dict[str, Any]] = []
    for err in exc.errors():
        loc = [str(item) for item in err.get("loc", [])]
        field = ".".join(loc[1:]) if len(loc) > 1 else (loc[0] if loc else "body")
        formatted_details.append({
            "field": field,
            "message": err.get("msg", "Validation error"),
            "type": err.get("type", "value_error"),
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": formatted_details,
            },
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "Internal server error",
            },
        },
    )


app.include_router(health_router)
app.include_router(schemes_router)
app.include_router(locations_router)
app.include_router(sources_router)
app.include_router(ingestion_router)
app.include_router(documents_router)
app.include_router(recommendations_router)
app.include_router(loan_calculator_router)
app.include_router(eligibility_check_router)
app.include_router(ai_router)

