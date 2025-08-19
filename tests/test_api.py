"""This is the test module for the Chatbot Debate API."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root() -> None:
    """Test the root endpoint of the Chatbot Debate API.

    It should return a welcome message.
    Returns: 200 status code and a JSON message.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from Chatbot Debate API"}
