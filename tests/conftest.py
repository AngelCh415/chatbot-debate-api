"""Conftest for pytest."""

import pytest
from fastapi.testclient import TestClient
from pytest import MonkeyPatch

from app.main import app, store
from app.settings import settings


@pytest.fixture(autouse=True)
def _force_mock_ai() -> None:
    """Force mock AI for all tests."""
    settings.USE_AI = False


@pytest.fixture(scope="function")
def client() -> TestClient:
    """Fixture to create a test client for FastAPI."""
    store._data.clear()
    return TestClient(app)


@pytest.fixture(autouse=True)
def fake_openai_key(monkeypatch: MonkeyPatch) -> None:
    """Set a fake OpenAI API key for tests."""
    monkeypatch.setenv("OPENAI_API_KEY", "test")


@pytest.fixture(autouse=True)
def _fake_openai_env(monkeypatch: MonkeyPatch) -> None:
    """Ensure a fake OpenAI API key is set for tests."""
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    settings.OPENAI_API_KEY = "test"
