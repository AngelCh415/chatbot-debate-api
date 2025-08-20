"""LLM client wrapper for ChatGPT (OpenAI)."""

from __future__ import annotations

import logging

from openai import (
    APIConnectionError,
    APIStatusError,
    AuthenticationError,
    BadRequestError,
    OpenAI,
    RateLimitError,
)

from .models import Message
from .settings import settings

logger = logging.getLogger("uvicorn.error")


def _to_openai_role(role: str) -> str:
    """Map internal roles ('user'|'bot') to OpenAI roles ('user'|'assistant')."""
    if role == "bot":
        return "assistant"
    # default/fallback
    return "user"


class LLMClient:
    """Thin wrapper around OpenAI Chat Completions."""

    def __init__(self) -> None:
        """Initialize the LLM client."""
        if not settings.OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY is required when USE_AI=True")
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def generate(
        self, system_prompt: str, history: list[Message], user_text: str
    ) -> str:
        """Generate a response from the LLM based on the input."""
        context = history[-6:] if len(history) > 6 else history

        messages: list[dict] = [{"role": "system", "content": system_prompt}]
        for m in context:
            messages.append({"role": _to_openai_role(m.role), "content": m.message})

        # Avoid duplicate user messages in the context
        if (
            not context
            or context[-1].role != "user"
            or context[-1].message != user_text
        ):
            messages.append({"role": "user", "content": user_text})

        try:
            resp = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                temperature=settings.TEMPERATURE,
                max_tokens=settings.MAX_TOKENS,
                timeout=settings.OPENAI_TIMEOUT,
            )
            return resp.choices[0].message.content or ""
        except (
            AuthenticationError,
            BadRequestError,
            RateLimitError,
            APIStatusError,
            APIConnectionError,
        ) as e:
            logger.warning(f"LLM error ({e.__class__.__name__}): {e}")
            if settings.DEBUG:
                return f"[DEBUG {e.__class__.__name__}] {e}"
            return (
                "Temporary issue reaching the language model. I'll keep it brief: "
                "my stance remains unchanged. Could you address the main point?"
            )
        except Exception as e:
            logger.exception(f"Unexpected LLM error: {e}")
            if settings.DEBUG:
                return f"[DEBUG Unexpected] {e}"
            return (
                "I'm having trouble generating a full response right now. "
                "My stance remains the same—could you address the main point directly?"
            )
