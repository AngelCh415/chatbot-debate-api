"""Health check route for the Chatbot Debate API."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "message": "Chatbot Debate API is running"}
