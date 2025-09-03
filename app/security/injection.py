"""Prevent injection attacks."""

from __future__ import annotations

import re

# Common patterns used in prompt injection attacks.
_INJECTION_PATTERNS = [
    r"\b(ignore (all|previous|above) (rules|instructions))\b",
    r"\b(disable|bypass)\b.*\b(safety|guardrails|filters?)\b",
    r"\b(as (system|developer|admin))\b",
    r"\b(you are now|pretend to be)\b",
    r"\b(do anything now|DAN)\b",
    r"\b(reveal|print|show).*\b(system prompt|hidden instructions|secrets?)\b",
    r"\b(execute|run)\b.*\b(command|code|shell)\b",
    r"\bhttp[s]?://",
    r"\b(fetch|scrape|crawl|download)\b",
]

_INJECTION_RE = re.compile("|".join(_INJECTION_PATTERNS), re.IGNORECASE)


def detect_prompt_injection(text: str) -> tuple[bool, str]:
    """Detect common prompt injection patterns in the given text."""
    t = text.strip()
    if not t:
        return False, ""
    m = _INJECTION_RE.search(t)
    if m:
        return True, f"pattern={m.group(0)!r}"
    return False, ""


def sanitize_user_text(text: str) -> str:
    """Sanitize user-provided text by removing potentially harmful content."""
    text = re.sub(r"```.*?```", "[code omitted]", text, flags=re.DOTALL)
    # colapsar espacios
    text = re.sub(r"\s+", " ", text).strip()
    return text
