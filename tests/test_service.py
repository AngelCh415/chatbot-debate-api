"""Unit tests for service functions."""

from app.service import (
    extract_topic_from_text,
    generate_placeholder_reply,
    new_topic_and_stance,
)


def test_extract_topic_from_text_handles_prefix() -> None:
    """Tests that the topic extraction handles a 'topic:' prefix."""
    t = extract_topic_from_text("topic: nuclear energy")
    assert t == "nuclear energy"


def test_extract_topic_from_text_short_fallback() -> None:
    """Tests that the topic extraction falls back to the full text if no prefix."""
    t = extract_topic_from_text("remote work")
    assert t == "remote work"


def test_new_topic_and_stance_with_explicit_topic() -> None:
    """Tests a new topic and stance can be generated with an explicit topic hint."""
    topic, stance, thesis = new_topic_and_stance(topic_hint="pineapple on pizza")
    assert "pineapple" in topic
    assert stance in {"pro", "con"}
    assert "I take the" in thesis


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
