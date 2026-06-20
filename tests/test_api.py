"""API endpoint tests."""

import pytest
from fastapi.testclient import TestClient
from src.chat_with_doc.api.main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_get_status(client):
    """Test the get status endpoint."""
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert "total_documents" in data
    assert "document_types" in data
    assert "filenames" in data


def test_clear_documents(client):
    """Test the clear documents endpoint."""
    response = client.post("/api/clear")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
