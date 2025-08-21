"""Chat endpoint for the Chatbot Debate API."""

from fastapi import APIRouter, HTTPException

from app.handlers.chat_handler import ConversationNotFoundError, handle_chat_message
from app.models.chat import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest) -> ChatResponse:
    """Handle chat messages."""
    try:
        return handle_chat_message(req)
    except ConversationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
