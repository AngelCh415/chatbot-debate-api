from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    """Test the root endpoint of the Chatbot Debate API"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from Chatbot Debate API"}
