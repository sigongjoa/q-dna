"""Tests for app/mcp/server.py"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
import sys

# Mock mathesis_core
class BaseMCPServer:
    """Mock BaseMCPServer"""
    def __init__(self, name=None, version=None):
        self.name = name
        self.version = version

mock_base = Mock()
mock_base.BaseMCPServer = BaseMCPServer
sys.modules['mathesis_core.mcp'] = Mock()
sys.modules['mathesis_core.mcp.server'] = mock_base

# Mock services
mock_ollama = Mock()
mock_tagging = Mock()
mock_crawler = Mock()
sys.modules['app.services.ollama_service'] = Mock(ollama_service=mock_ollama)
sys.modules['app.services.tagging_service'] = Mock(tagging_service=mock_tagging)
sys.modules['app.services.crawler_service'] = Mock(crawler_service=mock_crawler)

from app.mcp.server import Node2MCPServer


def test_mcp_server_init():
    """Test MCP server initialization"""
    server = Node2MCPServer()
    assert server is not None


@pytest.mark.asyncio
async def test_analyze_problem():
    """Test analyze_problem method"""
    server = Node2MCPServer()
    
    with patch('app.mcp.server.ollama_service') as mock_service:
        mock_service.generate_text = AsyncMock(return_value="This is a quadratic equation...")
        
        result = await server.analyze_problem("Solve x^2 + 5x + 6 = 0")
        
        assert "analysis" in result
        assert "quadratic" in result["analysis"].lower()
        mock_service.generate_text.assert_called_once()


@pytest.mark.asyncio
async def test_get_tag_recommendations():
    """Test get_tag_recommendations method"""
    server = Node2MCPServer()
    
    with patch('app.mcp.server.tagging_service') as mock_service:
        mock_service.get_tag_recommendations = AsyncMock(
            return_value=["algebra", "quadratic", "equations"]
        )
        
        result = await server.get_tag_recommendations("Solve x^2 + 5x + 6 = 0")
        
        assert "recommendations" in result
        assert isinstance(result["recommendations"], list)
        assert "algebra" in result["recommendations"]
        mock_service.get_tag_recommendations.assert_called_once()


@pytest.mark.asyncio
async def test_get_node2_status():
    """Test get_node2_status method"""
    server = Node2MCPServer()
    
    result = await server.get_node2_status()
    
    assert "status" in result
    assert result["status"] == "operational"
    assert result["engine"] == "Q-DNA"


@pytest.mark.asyncio
async def test_list_available_exam_sources():
    """Test list_available_exam_sources method"""
    server = Node2MCPServer()
    
    with patch('app.mcp.server.crawler_service') as mock_service:
        mock_service.list_available_sources = Mock(
            return_value=["KICE", "Seoul EDU", "Provincial EDU"]
        )
        
        result = await server.list_available_exam_sources()
        
        assert "sources" in result
        assert isinstance(result["sources"], list)
        assert "KICE" in result["sources"]
        mock_service.list_available_sources.assert_called_once()


@pytest.mark.asyncio
async def test_fetch_public_exams_success():
    """Test fetch_public_exams with successful download"""
    server = Node2MCPServer()
    
    with patch('app.mcp.server.crawler_service') as mock_service:
        mock_service.download_exam = Mock(
            return_value=["exam1.pdf", "exam2.pdf"]
        )
        
        result = await server.fetch_public_exams("KICE", "2025")
        
        assert "downloaded_files" in result
        assert "status" in result
        assert result["status"] == "success"
        assert len(result["downloaded_files"]) == 2
        mock_service.download_exam.assert_called_once_with("KICE", "2025")


@pytest.mark.asyncio
async def test_fetch_public_exams_failure():
    """Test fetch_public_exams with failed download"""
    server = Node2MCPServer()
    
    with patch('app.mcp.server.crawler_service') as mock_service:
        mock_service.download_exam = Mock(return_value=[])
        
        result = await server.fetch_public_exams("INVALID", "2025")
        
        assert result["status"] == "failed"
        assert result["downloaded_files"] == []


@pytest.mark.asyncio
async def test_fetch_public_exams_default_year():
    """Test fetch_public_exams uses default year"""
    server = Node2MCPServer()
    
    with patch('app.mcp.server.crawler_service') as mock_service:
        mock_service.download_exam = Mock(return_value=["exam.pdf"])
        
        result = await server.fetch_public_exams("KICE")
        
        mock_service.download_exam.assert_called_once_with("KICE", "2025")
