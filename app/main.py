"""Main application file for the debate chatbot API."""

from __future__ import annotations

import uuid

from fastapi import FastAPI, HTTPException

from .models import ChatRequest, ChatResponse, Message
from .service import (
    extract_topic_from_text,
    generate_placeholder_reply,
    new_topic_and_stance,
)
from .store import ConversationState, MemoryStore, trim_history

app = FastAPI(title="Chatbot Debate API")
store = MemoryStore()


@app.post("/chat", response_model=ChatResponse, summary="Chat entrypoint")
def chat(req: ChatRequest) -> ChatResponse:
    """Handle a chat turn, creating a conversation if needed.

    Rules:
    - If conversation_id is null, start a new conversation, define topic and stance.
    - Keep all responses tied to the initial thesis.
    - Maintain only the last five messages per role in the response history.
    """
    if not req.message.strip():
        raise HTTPException(status_code=422, detail="Message cannot be empty.")

    # Create or get conversation state
    if req.conversation_id is None:
        cid = str(uuid.uuid4())

        topic_hint = (req.topic or "").strip() or None
        if topic_hint is None:
            topic_hint = extract_topic_from_text(req.message)

        topic, stance, thesis = new_topic_and_stance(
            topic_hint=topic_hint, seed=req.message
        )
        state = ConversationState(topic=topic, stance=stance, thesis=thesis)
        store.set(cid, state)
    else:
        cid = req.conversation_id
        conv = store.get(cid)  # tipo: ConversationState | None
        if conv is None:
            raise HTTPException(status_code=404, detail="Conversation not found.")
        state = conv

    # Append user message
    state.history.append(Message(role="user", message=req.message))

    # Generate bot reply (placeholder v1)
    bot_text = generate_placeholder_reply(
        user_text=req.message,
        topic=state.topic,
        stance=state.stance,
        thesis=state.thesis,
    )
    state.history.append(Message(role="bot", message=bot_text))

    # Build trimmed response view
    view: list[Message] = trim_history(list(state.history), max_per_side=5)
    return ChatResponse(conversation_id=cid, message=view)
