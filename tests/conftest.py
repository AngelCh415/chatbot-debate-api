"""pytest configuration for the chatbot debate API tests."""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient
from pytest import MonkeyPatch

os.environ.setdefault("USE_AI", "false")
os.environ.setdefault("OPENAI_API_KEY", "dummy-key")

from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def client() -> TestClient:
    """Create a FastAPI test client for the application."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def fake_openai_key(monkeypatch: MonkeyPatch) -> None:
    """Set a fake OpenAI API key for tests."""
    monkeypatch.setenv("OPENAI_API_KEY", "test")
