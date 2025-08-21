"""Test cases for the main FastAPI application."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_root_health(client: TestClient) -> None:
    """Test the root endpoint for health check."""
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Chatbot Debate API is running" in resp.json().get("message", "")


def test_chat_new_conversation_creates_id(client: TestClient) -> None:
    """Test that a new conversation creates a unique ID."""
    resp = client.post(
        "/chat",
        json={
            "conversation_id": None,
            "message": "explain why Pepsi is better than Coke",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("conversation_id")
    assert isinstance(body.get("message"), list)


def test_chat_requires_non_empty_message(client: TestClient) -> None:
    """Test that an empty message returns a validation error."""
    resp = client.post("/chat", json={"conversation_id": None, "message": "   "})
    assert resp.status_code in (400, 422)  # depende de validaciones Pydantic


def test_first_message_defines_topic_from_free_text(client: TestClient) -> None:
    """Test that the first message defines the topic, stance, and thesis."""
    resp = client.post(
        "/chat",
        json={
            "conversation_id": None,
            "message": "explain why cats are better than dogs",
        },
    )
    assert resp.status_code == 200
    txt = " ".join(m["message"].lower() for m in resp.json()["message"])
    assert "cats" in txt or "cats are better" in txt


def test_history_capped_to_5_each_side(client: TestClient) -> None:
    """Test that the conversation history is capped to 5 messages per side."""
    r = client.post("/chat", json={"conversation_id": None, "message": "why pepsi"})
    cid = r.json()["conversation_id"]
    for _ in range(8):
        client.post("/chat", json={"conversation_id": cid, "message": "keep going"})
    r2 = client.post("/chat", json={"conversation_id": cid, "message": "last"})
    hist = r2.json()["message"]
    assert len([m for m in hist if m["role"] == "user"]) <= 5
    assert len([m for m in hist if m["role"] == "bot"]) <= 5


def test_nonexistent_conversation_returns_404(client: TestClient) -> None:
    """Test that a request to a non-existent conversation returns 404."""
    resp = client.post("/chat", json={"conversation_id": "no-such-id", "message": "hi"})
    assert resp.status_code == 404
