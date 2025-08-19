"""Service logic for the debate chatbot."""

from __future__ import annotations

import random
import re

# List of predefined debate topics
# This can be expanded or modified as needed.
# Topics should be concise and suitable for a debate format.
TOPICS = [
    "The Earth is flat",
    "Pineapple belongs on pizza",
    "Remote work is better than office work",
    "Artificial intelligence will improve society",
]


def extract_topic_from_text(text: str) -> str | None:
    """Try to infer a topic from free text.

    Examples accepted:
        "topic: nuclear energy"
        "debate: pineapple on pizza"
        "let's debate remote work"
    """
    text_l = text.lower().strip()

    # Patterns like "topic: xxx" or "debate: xxx"
    m = re.search(r"(?:topic|debate)\s*:\s*(.+)$", text_l)
    if m:
        return m.group(1).strip()

    # Fallback: short message likely is the topic itself
    if 0 < len(text_l) <= 60:
        return text_l

    return None


def new_topic_and_stance(
    topic_hint: str | None = None, seed: str | None = None
) -> tuple[str, str, str]:
    """Choose a topic and a stance (pro|con) with a concise thesis.

    Args:
        topic_hint: Optional explicit topic from the user.
        seed: Optional seed for deterministic choice when hint is missing.

    Returns:
        (topic, stance, thesis)
    """
    if topic_hint:
        topic = topic_hint.strip()
        # Add the topic to the pool if it's new
        if topic not in TOPICS:
            TOPICS.append(topic)
    else:
        random.seed(seed)
        topic = random.choice(TOPICS)

    stance = random.choice(["pro", "con"])
    thesis = f"I take the {stance} position on: {topic}."
    return topic, stance, thesis


def generate_placeholder_reply(
    user_text: str, topic: str, stance: str, thesis: str
) -> str:
    """Produce a short persuasive reply anchored to the original thesis."""
    opener = (
        "I hear your point, but let me clarify."
        if stance == "pro"
        else "I get your perspective, but I disagree for good reasons."
    )
    claim = f"My stance remains: {thesis}"
    reason = "Consider the broader evidence and practical trade-offs."
    nudge = "What part of that would you challenge specifically?"
    return f"{opener} {claim} {reason} {nudge}"
