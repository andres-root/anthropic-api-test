import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint returns welcome message."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to AioPy FastAPI!"}


def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "aiopy-api"


def test_async_demo():
    """Test the async demo endpoint."""
    response = client.get("/async-demo")
    assert response.status_code == 200
    data = response.json()
    
    assert "message" in data
    assert data["message"] == "Async tasks completed"
    assert "results" in data
    assert len(data["results"]) == 2
    assert data["total_tasks"] == 2
    assert "Task one completed" in data["results"]
    assert "Task two completed" in data["results"]


def test_get_user():
    """Test the parametrized user endpoint."""
    user_id = 123
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    
    assert data["user_id"] == user_id
    assert data["username"] == f"user_{user_id}"
    assert data["active"] is True


def test_get_user_invalid_id():
    """Test user endpoint with invalid ID."""
    response = client.get("/users/abc")
    assert response.status_code == 422  # Validation error


def test_echo_endpoint():
    """Test the echo endpoint."""
    test_data = {"name": "test", "value": 42, "active": True}
    response = client.post("/echo", json=test_data)
    assert response.status_code == 200
    data = response.json()
    
    assert data["received"] == test_data
    assert data["echo"] is True
    assert "timestamp" in data


def test_echo_endpoint_empty_data():
    """Test echo endpoint with empty data."""
    response = client.post("/echo", json={})
    assert response.status_code == 200
    data = response.json()
    assert data["received"] == {}
    assert data["echo"] is True


@pytest.mark.asyncio
async def test_async_timing():
    """Test that async operations complete in reasonable time."""
    import time
    
    start_time = time.time()
    response = client.get("/async-demo")
    end_time = time.time()
    
    assert response.status_code == 200
    # Should complete in about 2 seconds (max of concurrent 1s and 2s tasks)
    assert end_time - start_time < 3.0