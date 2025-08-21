"""LLM client wrapper for ChatGPT (OpenAI)."""

from __future__ import annotations

import logging
import random
import time
from collections.abc import Callable
from typing import TypeVar, cast

from openai import (
    APIConnectionError,
    APIStatusError,
    AuthenticationError,
    BadRequestError,
    OpenAI,
    RateLimitError,
)
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)

from app.core.settings import settings
from app.models.chat import Message

logger = logging.getLogger("uvicorn.error")
T = TypeVar("T")


def _with_backoff(fn: Callable[[], T], *, tries: int = 3) -> T:
    """Retry `fn` with exponential backoff + jitter for transient OpenAI errors.

    Retries on RateLimitError (429) and APIConnectionError (network).
    Lets the last exception bubble up; callers can format fallback text.
    """
    for i in range(tries - 1):  # leave last attempt for outside to catch
        try:
            return fn()
        except (RateLimitError, APIConnectionError) as e:
            sleep_s = (2**i) + random.random()  # 1, 2, 4 (+ jitter)
            logger.warning(
                "[LLM] transient error (%s), retry %d/%d in %.1fs: %s",
                e.__class__.__name__,
                i + 1,
                tries - 1,
                sleep_s,
                e,
            )
            time.sleep(sleep_s)
    # final attempt (if it fails, it raises to caller)
    return fn()


# helpers tipados (colócalos cerca de LLMClient o arriba)
def _sys_msg(content: str) -> ChatCompletionSystemMessageParam:
    """Create a system message for OpenAI ChatCompletion."""
    return {"role": "system", "content": content}


def _user_msg(content: str) -> ChatCompletionUserMessageParam:
    """Create a user message for OpenAI ChatCompletion."""
    return {"role": "user", "content": content}


def _asst_msg(content: str) -> ChatCompletionAssistantMessageParam:
    """Create an assistant message for OpenAI ChatCompletion."""
    return {"role": "assistant", "content": content}


def _to_openai_role(role: str) -> str:
    """Map internal roles ('user'|'bot') to OpenAI roles ('user'|'assistant')."""
    return "assistant" if role == "bot" else "user"


class LLMClient:
    """Thin wrapper around OpenAI Chat Completions."""

    def __init__(self, client: OpenAI | None = None) -> None:
        """Initialize the LLM client."""
        if client is not None:
            self.client = client
        else:
            if not settings.OPENAI_API_KEY:
                raise RuntimeError("OPENAI_API_KEY is required when USE_AI=True")
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def generate(
        self, system_prompt: str, history: list[Message], user_text: str
    ) -> str:
        """Generate a reply from the LLM given the prompt, history, and user text."""
        context = history[-6:] if len(history) > 6 else history

        messages: list[ChatCompletionMessageParam] = [
            cast(ChatCompletionMessageParam, _sys_msg(system_prompt))
        ]
        for m in context:
            role = _to_openai_role(m.role)
            if role == "assistant":
                messages.append(cast(ChatCompletionMessageParam, _asst_msg(m.message)))
            else:
                messages.append(cast(ChatCompletionMessageParam, _user_msg(m.message)))
        if (
            not context
            or context[-1].role != "user"
            or context[-1].message != user_text
        ):
            messages.append({"role": "user", "content": user_text})

        def _call() -> str:
            """Make the actual API call to OpenAI."""
            resp = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                temperature=settings.TEMPERATURE,
                max_tokens=settings.MAX_TOKENS,
                timeout=settings.OPENAI_TIMEOUT,
            )
            return resp.choices[0].message.content or ""

        try:
            return _with_backoff(_call, tries=3)
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
