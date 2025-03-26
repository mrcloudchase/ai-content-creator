import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
import asyncio
from app.main import app
from app.services.openai_service import OpenAIService, OpenAIServiceError
from app.routers.ai import get_openai_service

# Create a test client
client = TestClient(app)

# Create a mock service for testing
class MockOpenAIService:
    async def generate_completion(self, prompt, model=None, max_tokens=None, temperature=None):
        if not prompt:
            raise AssertionError("Prompt cannot be empty")
        
        return {
            "text": "This is a test response",
            "model": "gpt-3.5-turbo",
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "total_tokens": 30
            }
        }

# Override the dependency
async def override_get_openai_service():
    return MockOpenAIService()

# Replace the dependency for testing
app.dependency_overrides[get_openai_service] = override_get_openai_service

def test_generate_completion():
    """Test the /ai/completions endpoint"""
    response = client.post(
        "/api/v1/ai/completions",
        json={"prompt": "Test prompt"}
    )
    
    # Check status code
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    # Check response structure
    data = response.json()
    assert "text" in data, "Response should have a text field"
    assert "model" in data, "Response should have a model field"
    assert "usage" in data, "Response should have a usage field"
    
    # Check content
    assert data["text"] == "This is a test response", "Response text doesn't match expected output"
    assert data["model"] == "gpt-3.5-turbo", "Model doesn't match expected value"
    assert data["usage"]["prompt_tokens"] == 10, "Prompt tokens don't match expected value"

def test_empty_prompt():
    """Test the endpoint with an empty prompt"""
    response = client.post(
        "/api/v1/ai/completions",
        json={"prompt": ""}
    )
    
    # Check status code
    assert response.status_code == 400, f"Expected status code 400, got {response.status_code}"
    
    # Check error message
    data = response.json()
    assert "detail" in data, "Error response should have a detail key"
    assert "empty" in data["detail"].lower(), "Error should mention empty prompt"

# Create a failing service for error testing
class FailingOpenAIService:
    async def generate_completion(self, prompt, model=None, max_tokens=None, temperature=None):
        raise Exception("Service error")

def test_service_error():
    """Test handling of service errors"""
    # Override with failing service
    original_override = app.dependency_overrides[get_openai_service]
    
    try:
        # Set the failing service
        async def get_failing_service():
            return FailingOpenAIService()
            
        app.dependency_overrides[get_openai_service] = get_failing_service
        
        response = client.post(
            "/api/v1/ai/completions",
            json={"prompt": "Test prompt"}
        )
        
        # Check status code
        assert response.status_code == 500, f"Expected status code 500, got {response.status_code}"
    finally:
        # Restore the original override
        app.dependency_overrides[get_openai_service] = original_override 