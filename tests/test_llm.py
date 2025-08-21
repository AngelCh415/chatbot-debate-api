"""Test for the generate_ai_reply function."""

from typing import Any

from pytest import MonkeyPatch

import app.llm as llm_mod
from app import service
from app.models import Message
from app.service import generate_ai_reply


class DummyClient:
    """A dummy LLMClient that returns a fixed response for testing."""

    def generate(
        self, system_prompt: str, history: list[Message], user_text: str
    ) -> str:
        """Return a fixed response mimicking an AI reply."""
        return "Mocked AI reply."


class _DummyChoiceMsg:
    """A dummy choice message to mimic OpenAI response structure."""

    def __init__(self, content: str) -> None:
        """Initialize with content."""
        self.message = type("M", (), {"content": content})()


class _DummyResponse:
    """A dummy response to mimic OpenAI response structure."""

    def __init__(self, captured: list[dict[str, str]]) -> None:
        """Initialize with captured messages."""
        self.captured = captured
        self.choices: list[_DummyChoiceMsg] = [_DummyChoiceMsg("ok")]


class _DummyOpenAI:
    """A dummy OpenAI client to capture the messages sent to it."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the dummy client."""
        self._last_messages: list[dict[str, str]] = []
        self.chat = type(
            "Chat",
            (),
            {"completions": type("Completions", (), {"create": self.create})},
        )()

    def create(self, **kwargs: Any) -> _DummyResponse:
        """Capture the messages and return a dummy response."""
        messages = kwargs.get("messages")
        assert isinstance(messages, list)
        self._last_messages = messages  # captura
        return _DummyResponse(messages)


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


def test_roles_mapped_to_openai(monkeypatch: MonkeyPatch) -> None:
    """Test that roles are correctly mapped to OpenAI roles."""
    dummy = _DummyOpenAI()
    monkeypatch.setattr(llm_mod, "OpenAI", lambda api_key=None: dummy)

    client = llm_mod.LLMClient()
    out = client.generate(
        system_prompt="sys",
        history=[
            Message(role="user", message="hi"),
            Message(role="bot", message="hello"),
        ],
        user_text="next",
    )

    assert out == "ok"

    msgs = dummy._last_messages
    assert msgs[0]["role"] == "system"
    assert msgs[1]["role"] == "user"
    assert msgs[2]["role"] == "assistant"
    assert msgs[-1]["role"] == "user"


def test_backoff_retries_and_succeeds(monkeypatch: MonkeyPatch) -> None:
    """Test that the LLMClient retries on failure and eventually succeeds."""
    monkeypatch.setattr(llm_mod.time, "sleep", lambda s: None)
    monkeypatch.setattr(llm_mod, "OpenAI", lambda api_key=None: _DummyOpenAI())

    client = llm_mod.LLMClient()
    out = client.generate("sys", [Message(role="user", message="hi")], "next")
    assert out == "ok"
