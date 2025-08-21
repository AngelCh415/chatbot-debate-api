"""This module handles chat messages for a debate chatbot."""

from __future__ import annotations

import uuid

from fastapi import HTTPException

from app.core.settings import settings
from app.core.store import ConversationState, MemoryStore, trim_history
from app.models.chat import ChatRequest, ChatResponse, Message
from app.services.debate import (
    extract_topic_from_text,
    generate_ai_reply,
    generate_cohesive_reply,
    parse_topic_and_stance,
)

store = MemoryStore()


class ConversationNotFoundError(Exception):
    """Exception raised when a conversation is not found in the store."""

    pass


def handle_chat_message(req: ChatRequest) -> ChatResponse:
    """Handle incoming chat messages and generate AI replies."""
    if not req.message.strip():
        raise HTTPException(status_code=422, detail="Message cannot be empty.")

    # Create or get conversation state
    if req.conversation_id is None:
        cid = str(uuid.uuid4())

        topic_hint = (req.topic or "").strip() or None
        if topic_hint is None:
            topic_hint = extract_topic_from_text(req.message)

        topic, stance, thesis = parse_topic_and_stance(req.message)
        state = ConversationState(topic=topic, stance=stance, thesis=thesis)
        store.set(cid, state)
    else:
        cid = req.conversation_id
        conv = store.get(cid)
        if conv is None:
            raise HTTPException(status_code=404, detail="Conversation not found.")
        state = conv

    # Append user message
    state.history.append(Message(role="user", message=req.message))

    # Change if IA or cohesive reply is needed (v3)
    if settings.USE_AI:
        bot_text = generate_ai_reply(
            user_text=req.message,
            topic=state.topic,
            stance=state.stance,
            thesis=state.thesis,
            recent_history=list(state.history),
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

    # Build trimmed response view
    view: list[Message] = trim_history(list(state.history), max_per_side=5)
    return ChatResponse(conversation_id=cid, message=view)
