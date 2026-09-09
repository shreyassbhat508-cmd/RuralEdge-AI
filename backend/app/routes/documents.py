import logging
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Query, status
from app.schemas.document import RawDocumentResponse
from app.services.document_service import get_documents

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/documents", tags=["Raw Documents"])


@router.get("", response_model=List[RawDocumentResponse])
def read_documents(
    source_id: Optional[UUID] = Query(None, description="Filter by government source UUID"),
    document_type: Optional[str] = Query(None, description="Filter by document type (e.g. html, pdf)"),
    language: Optional[str] = Query(None, description="Filter by language code (e.g. en)"),
    processing_status: Optional[str] = Query(None, description="Filter by processing status (e.g. pending, processed)"),
):
    """
    GET /api/documents
    Retrieve raw documents with optional filters in a read-only manner.
    """
    try:
        documents = get_documents(
            source_id=source_id,
            document_type=document_type,
            language=language,
            processing_status=processing_status,
        )
        return documents
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to fetch raw documents at this time.",
        )
    except Exception as e:
        logger.error(f"Unexpected error in GET /api/documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred.",
        )
