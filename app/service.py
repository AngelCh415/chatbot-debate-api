"""Service logic for the debate chatbot."""

from __future__ import annotations

import re

from .models import Message

_STOPWORDS = {
    "the",
    "and",
    "for",
    "that",
    "this",
    "with",
    "have",
    "you",
    "but",
    "not",
    "are",
    "was",
    "has",
    "why",
    "better",
    "than",
    "can",
    "your",
    "about",
    "what",
    "when",
    "where",
    "which",
    "who",
    "would",
    "could",
    "should",
    "please",
    "explain",
    "tell",
    "more",
}


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


def parse_topic_and_stance(first_message: str) -> tuple[str, str, str]:
    """Infer topic, stance and thesis from the user's first free-form message.

    Heurísticas simples (no LLM):
      - "explain why X is better than Y"
      - "argue against X" / "why X is wrong"
      - Fallback -> topic = first_message, stance = "unknown", thesis = first_message

    Args:
        first_message: Raw first user message.

    Returns:
        (topic, stance, thesis)
    """
    text = first_message.strip()

    # Pattern: "... why X is better than Y"
    m = re.search(r"why\s+(.+?)\s+is\s+better\s+than\s+(.+)", text, flags=re.I)
    if m:
        x = m.group(1).strip()
        y = m.group(2).strip().rstrip(".!?")
        topic = f"{x} vs {y}"
        stance = f"pro {x}"
        thesis = f"{x} is better than {y}"
        return topic, stance, thesis

    # Pattern: "argue against X" / "debate against X"
    m = re.search(r"(argue|debate|explain)\s+against\s+(.+)", text, flags=re.I)
    if m:
        x = m.group(2).strip().rstrip(".!?")
        topic = x
        stance = f"con {x}"
        thesis = f"{x} is not correct"
        return topic, stance, thesis

    # Pattern: "why X is wrong"
    m = re.search(r"why\s+(.+?)\s+is\s+wrong", text, flags=re.I)
    if m:
        x = m.group(1).strip().rstrip(".!?")
        topic = x
        stance = f"con {x}"
        thesis = f"{x} is wrong"
        return topic, stance, thesis

    # Fallback: use the whole message as thesis/topic
    return text, "unknown", text


def _keywords(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z]{3,}", text.lower())
    return {w for w in words if w not in _STOPWORDS}


def _on_topic(user_text: str, thesis: str) -> bool:
    ku = _keywords(user_text)
    kt = _keywords(thesis)
    return len(ku & kt) >= 1


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


def generate_cohesive_reply(
    user_text: str,
    topic: str,
    stance: str,
    thesis: str,
    recent_history: list[Message] | None = None,
) -> str:
    """Return a short persuasive reply anchored to the thesis, with simple cohesion.

    - Always includes 'My stance remains: {thesis}.'
    - If user_text is off-topic, remind them to stay on topic.
    - Avoid repeating the last bot message.
    """
    claim = f"My stance remains: {thesis}."

    if not _on_topic(user_text, thesis):
        return (
            f"Let's stay on topic: {topic}. {claim} "
            "Could you address that point directly?"
        )

    # Avoid repeating the last bot message
    last_bot: str | None = None
    if recent_history:
        for m in reversed(recent_history):
            if m.role == "bot":
                last_bot = m.message
                break

    template_a = (
        "I see your point. {claim} One key reason is practical evidence "
        "from comparable cases. "
        "Can you challenge that with a concrete counterexample?"
    )
    template_b = (
        "{claim} From a trade-off perspective—costs, outcomes, and adoption—"
        "the conclusion still holds. Which aspect do you disagree with most?"
    )

    resp = template_a.replace("{claim}", claim)
    if last_bot and last_bot[:60] == resp[:60]:
        resp = template_b.replace("{claim}", claim)

    return resp
