import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from app import app
from models import ChatRequest, ChatMessage, MessageRole

client = TestClient(app)


def test_chat_completions_no_api_key():
    """Test chat endpoint without API key configured."""
    with patch.dict('os.environ', {}, clear=True):
        chat_request = {
            "messages": [
                {"role": "user", "content": "Hello, world!"}
            ]
        }
        response = client.post("/chat/completions", json=chat_request)
        assert response.status_code == 500
        assert "ANTHROPIC_API_KEY not configured" in response.json()["detail"]


@patch('app.anthropic_client')
def test_chat_completions_non_streaming(mock_client):
    """Test non-streaming chat completions."""
    # Mock response
    mock_response = AsyncMock()
    mock_response.content = [AsyncMock()]
    mock_response.content[0].text = "Hello! How can I help you today?"
    mock_response.model = "claude-3-5-sonnet-20241022"
    mock_response.usage.input_tokens = 10
    mock_response.usage.output_tokens = 20
    
    mock_client.messages.create.return_value = mock_response
    
    with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
        chat_request = {
            "messages": [
                {"role": "user", "content": "Hello, world!"}
            ],
            "stream": False
        }
        response = client.post("/chat/completions", json=chat_request)
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "assistant"
        assert data["content"] == "Hello! How can I help you today?"
        assert data["model"] == "claude-3-5-sonnet-20241022"
        assert "usage" in data


def test_chat_completions_validation():
    """Test request validation for chat completions."""
    with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
        # Test empty messages
        response = client.post("/chat/completions", json={"messages": []})
        assert response.status_code == 422
        
        # Test invalid role
        invalid_request = {
            "messages": [
                {"role": "invalid_role", "content": "Hello"}
            ]
        }
        response = client.post("/chat/completions", json=invalid_request)
        assert response.status_code == 422
        
        # Test missing content
        invalid_request = {
            "messages": [
                {"role": "user"}
            ]
        }
        response = client.post("/chat/completions", json=invalid_request)
        assert response.status_code == 422


def test_chat_completions_with_system_message():
    """Test chat completions with system message."""
    with patch('app.anthropic_client') as mock_client:
        mock_response = AsyncMock()
        mock_response.content = [AsyncMock()]
        mock_response.content[0].text = "I'm Claude, your AI assistant."
        mock_response.model = "claude-3-5-sonnet-20241022"
        mock_response.usage.input_tokens = 15
        mock_response.usage.output_tokens = 25
        
        mock_client.messages.create.return_value = mock_response
        
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            chat_request = {
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Who are you?"}
                ],
                "stream": False
            }
            response = client.post("/chat/completions", json=chat_request)
            assert response.status_code == 200
            
            # Verify system message was passed correctly
            mock_client.messages.create.assert_called_once()
            call_args = mock_client.messages.create.call_args
            assert "system" in call_args.kwargs
            assert call_args.kwargs["system"] == "You are a helpful assistant."


@patch('app.anthropic_client')
def test_chat_completions_streaming(mock_client):
    """Test streaming chat completions."""
    # Mock streaming response
    mock_stream = AsyncMock()
    mock_stream.__aenter__.return_value = mock_stream
    mock_stream.__aexit__.return_value = None
    
    # Mock events
    mock_events = [
        AsyncMock(type="message_start", message=AsyncMock(model="claude-3-5-sonnet-20241022")),
        AsyncMock(type="content_block_delta", delta=AsyncMock(text="Hello")),
        AsyncMock(type="content_block_delta", delta=AsyncMock(text=" there!")),
        AsyncMock(type="message_stop")
    ]
    mock_stream.__aiter__.return_value = mock_events
    
    mock_client.messages.stream.return_value = mock_stream
    
    with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
        chat_request = {
            "messages": [
                {"role": "user", "content": "Hello, world!"}
            ],
            "stream": True
        }
        response = client.post("/chat/completions", json=chat_request)
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/plain; charset=utf-8"


def test_chat_completions_custom_parameters():
    """Test chat completions with custom parameters."""
    with patch('app.anthropic_client') as mock_client:
        mock_response = AsyncMock()
        mock_response.content = [AsyncMock()]
        mock_response.content[0].text = "Custom response"
        mock_response.model = "claude-3-haiku-20240307"
        mock_response.usage.input_tokens = 10
        mock_response.usage.output_tokens = 20
        
        mock_client.messages.create.return_value = mock_response
        
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            chat_request = {
                "messages": [
                    {"role": "user", "content": "Test message"}
                ],
                "model": "claude-3-haiku-20240307",
                "max_tokens": 500,
                "temperature": 0.5,
                "stream": False
            }
            response = client.post("/chat/completions", json=chat_request)
            assert response.status_code == 200
            
            # Verify parameters were passed correctly
            mock_client.messages.create.assert_called_once()
            call_args = mock_client.messages.create.call_args
            assert call_args.kwargs["model"] == "claude-3-haiku-20240307"
            assert call_args.kwargs["max_tokens"] == 500
            assert call_args.kwargs["temperature"] == 0.5