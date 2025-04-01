import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.ai.customer_intent.routers.ai_customer_intent_router import router
from app.ai.core.services.ai_core_service import OpenAIServiceError

# Create test app
app = FastAPI()
app.include_router(router, prefix="/api/v1")
client = TestClient(app)

def test_router_endpoint():
    """Test that the router has the correct endpoint."""
    routes = [route for route in app.routes if route.path == "/api/v1/customer-intent"]
    assert len(routes) == 1
    assert routes[0].methods == {"POST"}

def test_generate_customer_intent_success():
    """Test generating customer intent with success."""
    # Mock the service method
    with patch('app.ai.customer_intent.services.ai_customer_intent_service.CustomerIntentService.generate_customer_intent', new_callable=AsyncMock) as mock_generate:
        # Configure the mock response
        mock_generate.return_value = {
            "intent": "As a user, I want to create reports because I need to analyze data.",
            "model": "gpt-3.5-turbo",
            "usage": {
                "prompt_tokens": 50,
                "completion_tokens": 20,
                "total_tokens": 70
            }
        }
        
        # Make request
        response = client.post(
            "/api/v1/customer-intent",
            json={
                "document_text": "Feature request: Generate PDF reports from data.",
                "user_type": "data analyst",
                "max_tokens": 200,
                "temperature": 0.7
            }
        )
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert "intent" in data
        assert "model" in data
        assert "usage" in data
        assert data["intent"] == "As a user, I want to create reports because I need to analyze data."
        
        # Verify function was called with correct parameters
        mock_generate.assert_called_once()
        call_args = mock_generate.call_args[1]
        assert call_args["document_text"] == "Feature request: Generate PDF reports from data."
        assert call_args["user_type"] == "data analyst"
        assert call_args["max_tokens"] == 200
        assert call_args["temperature"] == 0.7

def test_generate_customer_intent_with_defaults():
    """Test generating customer intent with default parameters."""
    # Mock the service method
    with patch('app.ai.customer_intent.services.ai_customer_intent_service.CustomerIntentService.generate_customer_intent', new_callable=AsyncMock) as mock_generate:
        # Configure the mock response
        mock_generate.return_value = {
            "intent": "As a user, I want to create reports because I need to analyze data.",
            "model": "gpt-3.5-turbo",
            "usage": {
                "prompt_tokens": 50,
                "completion_tokens": 20,
                "total_tokens": 70
            }
        }
        
        # Make request with minimal parameters
        response = client.post(
            "/api/v1/customer-intent",
            json={
                "document_text": "Feature request: Generate PDF reports from data."
            }
        )
        
        # Check response
        assert response.status_code == 200
        
        # Verify function was called with default parameters where not specified
        mock_generate.assert_called_once()
        call_args = mock_generate.call_args[1]
        assert call_args["document_text"] == "Feature request: Generate PDF reports from data."
        assert call_args["user_type"] is None
        assert call_args["max_tokens"] == 150
        assert call_args["temperature"] == 0.5

def test_generate_customer_intent_openai_error():
    """Test error handling when OpenAI service fails."""
    # Mock the service method to raise OpenAIServiceError
    with patch('app.ai.customer_intent.services.ai_customer_intent_service.CustomerIntentService.generate_customer_intent',
              side_effect=OpenAIServiceError("OpenAI API unavailable")) as mock_generate:
        
        # Make request
        response = client.post(
            "/api/v1/customer-intent",
            json={
                "document_text": "Feature request: Generate PDF reports from data."
            }
        )
        
        # Check response
        assert response.status_code == 503
        data = response.json()
        assert "detail" in data
        assert "OpenAI API unavailable" in data["detail"]

def test_generate_customer_intent_unexpected_error():
    """Test error handling for unexpected errors."""
    # Mock the service method to raise unexpected error
    with patch('app.ai.customer_intent.services.ai_customer_intent_service.CustomerIntentService.generate_customer_intent',
              side_effect=Exception("Unexpected error")) as mock_generate:
        
        # Make request
        response = client.post(
            "/api/v1/customer-intent",
            json={
                "document_text": "Feature request: Generate PDF reports from data."
            }
        )
        
        # Check response
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "unexpected error" in data["detail"].lower() 