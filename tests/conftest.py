"""Conftest for pytest."""

import pytest
from fastapi.testclient import TestClient

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
