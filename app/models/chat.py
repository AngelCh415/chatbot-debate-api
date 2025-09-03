"""Pydantic models for the Chatbot Debate API."""

from collections import deque
from dataclasses import dataclass, field
from typing import Literal

from pydantic import BaseModel, Field

Role = Literal["user", "bot"]


class ChatRequest(BaseModel):
    """Input schema for the /chat endpoint."""

    conversation_id: str | None = Field(
        default=None, description="Existing conversation id or null to start"
    )
    message: str = Field(..., min_length=1, max_length=2000)
    topic: str | None = Field(
        default=None,
        description="Optional user-provided debate topic for a new conversation",
        max_length=200,
    )


class Message(BaseModel):
    """A single utterance in the conversation."""

    role: Role
    message: str


class ChatResponse(BaseModel):
    """Output schema for the chat."""

    conversation_id: str
    message: list[Message]


@dataclass
class ConversationState:
    """Holds topic, stance and rolling history for a conversation."""

    # topic is the subject of the debate
    topic: str
    # stance can be "pro" or "con"
    stance: str
    # thesis is the main argument or position
    thesis: str
    # history is a rolling history of messages in the conversation
    history: deque[Message] = field(default_factory=deque)
