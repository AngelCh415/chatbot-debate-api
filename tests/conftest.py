"""Conftest for pytest."""

import pytest
from fastapi.testclient import TestClient

from app.main import app, store


@pytest.fixture(scope="function")
def client() -> TestClient:
    """Fixture to create a test client for FastAPI."""
    store._data.clear()
    return TestClient(app)
