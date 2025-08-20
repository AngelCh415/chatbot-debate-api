"""Unit test for main of the API."""

from fastapi.testclient import TestClient


def test_chat_new_conversation_creates_id(client: TestClient) -> None:
    """Test that starting a new conversation returns a new ID and bot message."""
    resp = client.post("/chat", json={"conversation_id": None, "message": "start"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["conversation_id"]
    assert body["message"][-1]["role"] == "bot"


def test_chat_requires_non_empty_message(client: TestClient) -> None:
    """Test that an empty message returns a 422 error."""
    resp = client.post("/chat", json={"conversation_id": None, "message": "   "})
    assert resp.status_code == 422
    assert resp.json()["detail"] == "Message cannot be empty."


def test_first_message_defines_topic_from_free_text(client: TestClient) -> None:
    """Topic and stance should be inferred from the user's first free-form message."""
    resp = client.post(
        "/chat",
        json={
            "conversation_id": None,
            "message": "explain why nuclear energy is better than fossil fuels",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    text = " ".join(m["message"].lower() for m in body["message"])
    assert "nuclear energy is better than fossil fuels" in text


def test_chat_infers_topic_from_first_message(client: TestClient) -> None:
    """Test that the topic can be inferred from the first user message."""
    resp = client.post(
        "/chat",
        json={
            "conversation_id": None,
            "message": "topic: remote work boosts productivity",
        },
    )
    assert resp.status_code == 200
    text = " ".join(m["message"].lower() for m in resp.json()["message"])
    assert "remote work" in text


def test_history_capped_to_5_each_side(client: TestClient) -> None:
    """Test that the conversation history is trimmed to 5 messages per side."""
    r = client.post("/chat", json={"conversation_id": None, "message": "start"})
    cid = r.json()["conversation_id"]

    for i in range(8):
        client.post("/chat", json={"conversation_id": cid, "message": f"turn {i}"})

    final = client.post("/chat", json={"conversation_id": cid, "message": "last"})
    msgs = final.json()["message"]

    assert len(msgs) <= 10
    user_count = sum(1 for m in msgs if m["role"] == "user")
    bot_count = sum(1 for m in msgs if m["role"] == "bot")
    assert user_count <= 5 and bot_count <= 5
    assert msgs[-1]["role"] == "bot"


def test_nonexistent_conversation_returns_404(client: TestClient) -> None:
    """Test that using a nonexistent conversation ID returns a 404 error."""
    resp = client.post(
        "/chat", json={"conversation_id": "does-not-exist", "message": "hello"}
    )
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Conversation not found."


def test_chat_reconduces_when_off_topic(client: TestClient) -> None:
    """Test that the bot redirects off-topic messages back to the topic."""
    r = client.post(
        "/chat",
        json={
            "conversation_id": None,
            "message": "explain why Pepsi is better than Coke",
        },
    )
    cid = r.json()["conversation_id"]

    r2 = client.post(
        "/chat", json={"conversation_id": cid, "message": "what is your name?"}
    )
    txt = " ".join(m["message"] for m in r2.json()["message"])
    assert "Let's stay on topic" in txt
