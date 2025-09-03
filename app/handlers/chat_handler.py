"""This module handles chat messages for a debate chatbot."""

from __future__ import annotations

import uuid
from collections import deque

from fastapi import HTTPException

from app.core.settings import settings
from app.models.chat import ChatRequest, ChatResponse, ConversationState, Message
from app.services.debate import (
    generate_ai_reply,
    generate_cohesive_reply,
    parse_topic_and_stance,
)
from app.storage import get_store

store = get_store()


class ConversationNotFoundError(Exception):
    """Exception raised when a conversation is not found in the store."""

    pass


def _last_user_message(state: ConversationState) -> str | None:
    """Return the last user message *before* the current turn."""
    for m in reversed(state.history):
        if m.role == "user":
            return m.message
    return None


def handle_chat_message(req: ChatRequest) -> ChatResponse:
    """Handle incoming chat messages and generate AI replies."""
    user_text = req.message.strip()
    if not user_text:
        raise HTTPException(status_code=422, detail="Message cannot be empty.")

    # 1) Create or load conversation state
    if req.conversation_id is None:
        cid = str(uuid.uuid4())
        topic, stance, thesis = parse_topic_and_stance(user_text)
        state = ConversationState(
            topic=topic,
            stance=stance,
            thesis=thesis,
            history=deque(),
        )
        store.set(cid, state)
    else:
        cid = req.conversation_id
        state_opt = store.get(cid)
        if state_opt is None:
            raise HTTPException(status_code=404, detail="Conversation not found.")
        state = state_opt

    prev_user_text = _last_user_message(state)

    state.history.append(Message(role="user", message=user_text))

    if settings.USE_AI:
        bot_text = generate_ai_reply(
            user_text=user_text,
            topic=state.topic,
            stance=state.stance,
            thesis=state.thesis,
            recent_history=list(state.history),
            prev_user_text=prev_user_text,
        )
    else:
        bot_text = generate_cohesive_reply(
            user_text=req.message,
            topic=state.topic,
            stance=state.stance,
            thesis=state.thesis,
            recent_history=list(state.history),
        )
    state.history.append(Message(role="bot", message=bot_text))

    store.set(cid, state)

    trimmed = store.trim(cid, max_per_side=5)
    state = trimmed or state
    store.set(cid, state)

    messages = [{"role": m.role, "message": m.message} for m in state.history]

    return ChatResponse(conversation_id=cid, message=messages)
