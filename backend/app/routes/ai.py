import logging
import uuid
from fastapi import APIRouter, HTTPException, status
from app.schemas.ai import AIChatRequest, AIChatResponse
from app.services.ai_service import generate_ai_chat_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ai", tags=["AI Assistant"])


@router.post("/chat", response_model=AIChatResponse)
def ai_chat_endpoint(request: AIChatRequest):
    """
    POST /api/ai/chat
    Provides a safe, grounded AI assistant layer powered by Gemini to explain government schemes in simple language.
    Does not determine official eligibility or alter database records.
    """
    if request.scheme_id and request.scheme_id.strip():
        try:
            uuid.UUID(request.scheme_id.strip())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid scheme_id UUID format.",
            )

    try:
        response = generate_ai_chat_response(request)
        return response
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheme not found.",
        )
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI assistant is temporarily unavailable.",
        )
    except Exception as e:
        logger.error(f"Unexpected error in POST /api/ai/chat: {type(e).__name__}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI assistant is temporarily unavailable.",
        )
