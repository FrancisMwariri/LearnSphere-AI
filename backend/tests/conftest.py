import pytest
from fastapi.testclient import TestClient

from app.services.session_store import session_store
from main import app


@pytest.fixture
def client():
    session_store.clear()
    with TestClient(app) as test_client:
        yield test_client
    session_store.clear()
