"""Tests for app/main.py"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
import sys

# Mock dependencies
mock_ollama = Mock()
mock_ollama.health_check = AsyncMock(return_value=True)
sys.modules['app.services.ollama_service'] = Mock(ollama_service=mock_ollama)

# Mock database
mock_engine = Mock()
mock_engine.begin = AsyncMock()
mock_engine.dispose = AsyncMock()
sys.modules['app.core.database'].engine = mock_engine

from app.main import app


@pytest.fixture
def client():
    """Test client"""
    return TestClient(app)


def test_read_root(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Q-DNA" in data["message"]
    assert "version" in data
    assert "docs" in data


@pytest.mark.asyncio
async def test_health_check(client):
    """Test health check endpoint"""
    with patch('app.main.ollama_service') as mock_service:
        mock_service.health_check = AsyncMock(return_value=True)
        
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "database" in data
        assert "ollama" in data


@pytest.mark.asyncio
async def test_health_check_ollama_down(client):
    """Test health check when Ollama is down"""
    with patch('app.main.ollama_service') as mock_service:
        mock_service.health_check = AsyncMock(return_value=False)
        
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["ollama"] == "disconnected"


def test_app_title():
    """Test app has correct title"""
    assert app.title == "Q-DNA API"


def test_app_has_cors():
    """Test CORS middleware is configured"""
    middlewares = [m for m in app.user_middleware]
    assert len(middlewares) > 0


def test_static_mount():
    """Test static files are mounted"""
    routes = [route.path for route in app.routes]
    assert any("/static" in route for route in routes)


def test_api_router_included():
    """Test API router is included"""
    routes = [route.path for route in app.routes]
    assert any("/api/v1" in route for route in routes)
