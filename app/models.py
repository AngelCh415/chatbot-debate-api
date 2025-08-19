"""Pydantic models for the Chatbot Debate API."""

from typing import Literal

from pydantic import BaseModel, Field

Role = Literal["user", "bot"]


class ChatRequest(BaseModel):
    """Input schema for the /chat endpoint."""

    conversation_id: str | None = Field(
        default=None, description="Existing conversation id or null to start"
    )
    message: str = Field(..., min_length=1, max_length=2000)


class Message(BaseModel):
    """A single utterance in the conversation."""

    role: Role
    message: str


class ChatResponse(BaseModel):
    """Output schema for the chat."""

    conversation_id: str
    message: list[Message]
