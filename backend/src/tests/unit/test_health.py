"""Unit tests for health check endpoint."""
import pytest
from httpx import AsyncClient
from datetime import datetime

pytestmark = pytest.mark.asyncio

async def test_health_check_success(client: AsyncClient):
    """Test successful health check response."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "operational"
    assert data["database_connected"] is True
    assert data["version"] == "1.0.0"
    assert isinstance(datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00")), datetime)

async def test_root_endpoint(client: AsyncClient):
    """Test root endpoint response."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    
    assert data["name"] == "AI Analytics Platform API"
    assert data["version"] == "1.0.0"
    assert data["status"] == "operational" 