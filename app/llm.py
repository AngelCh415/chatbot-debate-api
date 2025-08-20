"""LLM client wrapper for ChatGPT (OpenAI)."""

from __future__ import annotations

from openai import APIConnectionError, OpenAI, RateLimitError

from .models import Message
from .settings import settings


class LLMClient:
    """Thin wrapper around OpenAI Chat Completions."""

    def __init__(self) -> None:
        """Initialize the LLM client."""
        if not settings.OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY is required when USE_AI=True")
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def generate(
        self,
        system_prompt: str,
        history: list[Message],
        user_text: str,
    ) -> str:
        """Generate one reply with short timeout and a bit of temperature."""
        # Use the last 6 messages from history to provide context
        context = history[-6:] if len(history) > 6 else history

        messages = [{"role": "system", "content": system_prompt}]
        for m in context:
            messages.append({"role": m.role, "content": m.message})
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
        except (APIConnectionError, RateLimitError):
            # Fallback response in case of connection issues or rate limits
            return (
                "Temporary issue reaching the language model. I'll keep it brief: "
                "my stance remains unchanged. Could you address the main point?"
            )
