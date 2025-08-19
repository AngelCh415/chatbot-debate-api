"""Unit tests for service functions."""

from fastapi.testclient import TestClient

from app.service import (
    extract_topic_from_text,
    generate_placeholder_reply,
    parse_topic_and_stance,
)


def test_first_message_defines_topic_and_stance(client: TestClient) -> None:
    """Test that the first message defines the topic and stance."""
    r = client.post(
        "/chat",
        json={
            "conversation_id": None,
            "message": "explain why Pepsi is better than Coke",
        },
    )
    assert r.status_code == 200
    body = r.json()
    text = " ".join(m["message"].lower() for m in body["message"])
    # Debe reflejar la tesis "pepsi is better than coke"
    assert "pepsi is better than coke" in text


def test_extract_topic_from_text_handles_prefix() -> None:
    """Tests that the topic extraction handles a 'topic:' prefix."""
    t = extract_topic_from_text("topic: nuclear energy")
    assert t == "nuclear energy"


def test_extract_topic_from_text_short_fallback() -> None:
    """Tests that the topic extraction falls back to the full text if no prefix."""
    t = extract_topic_from_text("remote work")
    assert t == "remote work"


def test_parse_topic_and_stance_fallback() -> None:
    """If no pattern matches, the whole message should be used as fallback."""
    msg = "Let's debate about remote work in general"
    topic, stance, thesis = parse_topic_and_stance(msg)
    assert topic == msg
    assert stance == "unknown"
    assert thesis == msg


def test_generate_placeholder_reply_mentions_thesis() -> None:
    """Tests that the placeholder reply mentions the thesis."""
    reply = generate_placeholder_reply(
        user_text="why?",
        topic="remote work",
        stance="pro",
        thesis="I take the pro position on: remote work.",
    )
    assert "My stance remains:" in reply
    assert "remote work" in reply or "stance" in reply
