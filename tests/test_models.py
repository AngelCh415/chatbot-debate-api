"""Unit tests for the model definitions."""

import pytest
from pydantic import ValidationError

from app.models.chat import ChatRequest, Message


def test_chat_request_accepts_null_conversation_id() -> None:
    """Test that ChatRequest accepts None for conversation_id."""
    req = ChatRequest(conversation_id=None, message="hello")
    assert req.conversation_id is None
    assert req.message == "hello"


def test_chat_request_rejects_empty_message() -> None:
    """Test that ChatRequest raises ValidationError for empty message."""
    with pytest.raises(ValidationError):
        ChatRequest(conversation_id=None, message="")


def test_message_model_user_and_bot_roles() -> None:
    """Test that Message model accepts 'user' and 'bot' roles."""
    m1 = Message(role="user", message="hi")
    m2 = Message(role="bot", message="hello")
    assert m1.role == "user" and m2.role == "bot"
