"""Test for the generate_ai_reply function."""

from pytest import MonkeyPatch

from app import service
from app.models import Message
from app.service import generate_ai_reply


class DummyClient:
    """A dummy LLMClient that returns a fixed response for testing."""

    def generate(
        self, system_prompt: str, history: list[Message], user_text: str
    ) -> str:
        """Return a fixed response mimicking an AI reply."""
        return "Mocked AI reply anchored to thesis."


def test_generate_ai_reply_with_monkeypatch(monkeypatch: MonkeyPatch) -> None:
    """Test the generate_ai_reply function with a mocked LLMClient."""
    # Mock the LLMClient to return a fixed response

    monkeypatch.setattr(service, "LLMClient", lambda: DummyClient())
    text = generate_ai_reply(
        user_text="why?",
        topic="Pepsi vs Coke",
        stance="pro Pepsi",
        thesis="Pepsi is better than Coke",
        recent_history=[Message(role="user", message="start")],
    )
    assert "Mocked AI reply" in text
