"""Tests for app/grpc/server.py"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
import sys
import uuid

# Mock mathesis_core
mock_common_pb2 = Mock()
mock_common_pb2_grpc = Mock()
mock_common_pb2.Question = Mock
mock_common_pb2_grpc.MathesisServiceServicer = object
sys.modules['mathesis_core.grpc'] = Mock()
sys.modules['mathesis_core.grpc.common_pb2'] = mock_common_pb2
sys.modules['mathesis_core.grpc.common_pb2_grpc'] = mock_common_pb2_grpc

from app.grpc.server import Node2ServiceServicer, serve_grpc


@pytest.mark.asyncio
async def test_servicer_init():
    """Test Node2ServiceServicer initialization"""
    servicer = Node2ServiceServicer()
    assert servicer is not None


@pytest.mark.asyncio
async def test_get_question_success():
    """Test GetQuestion with successful database query"""
    servicer = Node2ServiceServicer()
    
    # Mock request
    mock_request = Mock()
    test_uuid = str(uuid.uuid4())
    mock_request.id = test_uuid
    
    # Mock context
    mock_context = Mock()
    
    # Mock database
    mock_question = Mock()
    mock_question.question_id = uuid.UUID(test_uuid)
    mock_question.content_stem = "What is 2+2?"
    mock_question.answer_key = "4"
    
    mock_result = Mock()
    mock_result.scalars = Mock(return_value=Mock(first=Mock(return_value=mock_question)))
    
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.__aenter__ = AsyncMock(return_value=mock_db)
    mock_db.__aexit__ = AsyncMock(return_value=None)
    
    with patch('app.grpc.server.SessionLocal', return_value=mock_db), \
         patch('app.grpc.server.common_pb2.Question', return_value=Mock()) as mock_q_class:
        
        result = await servicer.GetQuestion(mock_request, mock_context)
        
        # Verify Question was called with correct data
        mock_q_class.assert_called_once()


@pytest.mark.asyncio
async def test_get_question_not_found():
    """Test GetQuestion when question not found"""
    servicer = Node2ServiceServicer()
    
    mock_request = Mock()
    mock_request.id = str(uuid.uuid4())
    
    mock_context = Mock()
    
    # Mock database returning None
    mock_result = Mock()
    mock_result.scalars = Mock(return_value=Mock(first=Mock(return_value=None)))
    
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.__aenter__ = AsyncMock(return_value=mock_db)
    mock_db.__aexit__ = AsyncMock(return_value=None)
    
    with patch('app.grpc.server.SessionLocal', return_value=mock_db), \
         patch('app.grpc.server.common_pb2.Question', return_value=Mock()) as mock_q_class:
        
        result = await servicer.GetQuestion(mock_request, mock_context)
        
        # Verify NOT_FOUND was set
        mock_context.set_code.assert_called_once()


@pytest.mark.asyncio
async def test_get_question_database_error():
    """Test GetQuestion when database fails (simulation mode)"""
    servicer = Node2ServiceServicer()
    
    mock_request = Mock()
    mock_request.id = "test-id"
    
    mock_context = Mock()
    
    # Mock database raising exception
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(side_effect=Exception("DB error"))
    mock_db.__aenter__ = AsyncMock(return_value=mock_db)
    mock_db.__aexit__ = AsyncMock(return_value=None)
    
    with patch('app.grpc.server.SessionLocal', return_value=mock_db), \
         patch('app.grpc.server.common_pb2.Question', return_value=Mock()) as mock_q_class:
        
        result = await servicer.GetQuestion(mock_request, mock_context)
        
        # Verify simulation response was returned
        mock_q_class.assert_called_once()
        call_kwargs = mock_q_class.call_args[1]
        assert call_kwargs['id'] == "test-id"
        assert "derivative" in call_kwargs['text'].lower()


@pytest.mark.asyncio
async def test_get_question_invalid_uuid():
    """Test GetQuestion with invalid UUID (falls back to simulation)"""
    servicer = Node2ServiceServicer()
    
    mock_request = Mock()
    mock_request.id = "not-a-valid-uuid"
    
    mock_context = Mock()
    
    with patch('app.grpc.server.common_pb2.Question', return_value=Mock()) as mock_q_class:
        result = await servicer.GetQuestion(mock_request, mock_context)
        
        # Verify simulation response was returned
        mock_q_class.assert_called_once()


@pytest.mark.asyncio
async def test_serve_grpc():
    """Test serve_grpc server initialization"""
    with patch('app.grpc.server.grpc.aio.server') as mock_server_func:
        mock_server = Mock()
        mock_server.start = AsyncMock()
        mock_server.wait_for_termination = AsyncMock()
        mock_server_func.return_value = mock_server
        
        with patch('app.grpc.server.common_pb2_grpc.add_MathesisServiceServicer_to_server') as mock_add:
            # Start server in background
            import asyncio
            task = asyncio.create_task(serve_grpc())
            
            await asyncio.sleep(0.1)
            task.cancel()
            
            try:
                await task
            except asyncio.CancelledError:
                pass
            
            # Verify server was configured
            mock_server_func.assert_called_once()
            mock_add.assert_called_once()
            mock_server.add_insecure_port.assert_called_once_with("[::]:50052")
            mock_server.start.assert_called_once()
