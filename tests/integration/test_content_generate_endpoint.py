import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from app.main import app
from app.ai.content_generate.models.content_generate_model import (
    ContentTypeRequest,
    ContentGenerateRequest,
    GeneratedContent,
    ContentGenerateResponse
)

client = TestClient(app)

class TestContentGenerateEndpoint:
    """Integration tests for the content generation endpoint"""
    
    @patch("app.ai.content_generate.routers.content_generate_router.ai_service")
    @patch("app.ai.content_generate.routers.content_generate_router.tokenizer_service")
    def test_generate_content_success(self, mock_tokenizer_service, mock_ai_service):
        """Test successful content generation with valid input"""
        # Mock tokenizer service
        mock_token_info = {
            "model": "gpt-4",
            "model_family": "gpt",
            "capabilities": {"supports_functions": True},
            "usage": {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150},
            "model_limit": 4000,
            "token_count": 1000,
            "tokens_remaining": 3000,
            "percentage_used": 25
        }
        mock_tokenizer_service.validate_tokens.return_value = mock_token_info
        
        # Mock AI service
        mock_completion = {"text": "# Generated Tutorial\n\nThis is a test tutorial."}
        mock_ai_service.generate_completion = AsyncMock(return_value=mock_completion)
        
        # Request data
        request_data = {
            "intent": "As a developer, I want to create a REST API because it will help me serve data to clients.",
            "text_used": "This is sample text about REST APIs and how to build them with FastAPI.",
            "content_types": [
                {
                    "type": "tutorial",
                    "title": "Building a REST API with FastAPI"
                }
            ]
        }
        
        # Make request
        response = client.post("/api/v1/content-generate", json=request_data)
        
        # Verify response
        assert response.status_code == 200
        
        data = response.json()
        assert "generated_content" in data
        assert len(data["generated_content"]) == 1
        assert data["generated_content"][0]["type"] == "tutorial"
        assert data["generated_content"][0]["title"] == "Building a REST API with FastAPI"
        assert data["generated_content"][0]["content"] == "# Generated Tutorial\n\nThis is a test tutorial."
        
        # Verify metadata
        assert data["model"] == "gpt-4"
        assert data["model_family"] == "gpt"
        assert "capabilities" in data
        assert "usage" in data
        assert "token_limit" in data
        assert "token_count" in data
        assert "remaining_tokens" in data
        assert data["text_used"] == request_data["text_used"]
    
    @patch("app.ai.content_generate.routers.content_generate_router.ai_service")
    @patch("app.ai.content_generate.routers.content_generate_router.tokenizer_service")
    def test_generate_content_multiple_types(self, mock_tokenizer_service, mock_ai_service):
        """Test generating content for multiple content types"""
        # Mock tokenizer service
        mock_token_info = {
            "model": "gpt-4",
            "model_family": "gpt",
            "capabilities": {"supports_functions": True},
            "usage": {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150},
            "model_limit": 4000,
            "token_count": 1000,
            "tokens_remaining": 3000,
            "percentage_used": 25
        }
        mock_tokenizer_service.validate_tokens.return_value = mock_token_info
        
        # Mock AI service with different responses for each content type
        mock_completions = [
            {"text": "# Generated Tutorial\n\nThis is a test tutorial."},
            {"text": "# How to Use FastAPI\n\nSteps to create REST APIs."}
        ]
        mock_ai_service.generate_completion = AsyncMock(side_effect=mock_completions)
        
        # Request data with multiple content types
        request_data = {
            "intent": "As a developer, I want to create a REST API because it will help me serve data to clients.",
            "text_used": "This is sample text about REST APIs and how to build them with FastAPI.",
            "content_types": [
                {
                    "type": "tutorial",
                    "title": "Building a REST API with FastAPI"
                },
                {
                    "type": "how-to",
                    "title": None  # Test auto-extraction of title
                }
            ]
        }
        
        # Make request
        response = client.post("/api/v1/content-generate", json=request_data)
        
        # Verify response
        assert response.status_code == 200
        
        data = response.json()
        assert "generated_content" in data
        assert len(data["generated_content"]) == 2
        
        # Check first content
        assert data["generated_content"][0]["type"] == "tutorial"
        assert data["generated_content"][0]["title"] == "Building a REST API with FastAPI"
        assert data["generated_content"][0]["content"] == "# Generated Tutorial\n\nThis is a test tutorial."
        
        # Check second content
        assert data["generated_content"][1]["type"] == "how-to"
        assert data["generated_content"][1]["title"] == "How to Use FastAPI"  # Extracted from content
        assert data["generated_content"][1]["content"] == "# How to Use FastAPI\n\nSteps to create REST APIs."
    
    def test_generate_content_invalid_request(self):
        """Test error handling with invalid request data"""
        # Missing required fields
        request_data = {
            "intent": "As a developer, I want to create a REST API.",
            # Missing text_used
            "content_types": [
                {
                    "type": "tutorial",
                    "title": "Building a REST API"
                }
            ]
        }
        
        # Make request
        response = client.post("/api/v1/content-generate", json=request_data)
        
        # Verify response
        assert response.status_code == 422  # Validation error
        
        data = response.json()
        assert "detail" in data
        # Check that the validation error mentions the missing field
        assert any("text_used" in error["loc"] for error in data["detail"])
    
    def test_generate_content_invalid_content_type(self):
        """Test error handling with invalid content type"""
        # Invalid content type
        request_data = {
            "intent": "As a developer, I want to create a REST API.",
            "text_used": "Sample text.",
            "content_types": [
                {
                    "type": "invalid_type",  # This type doesn't exist
                    "title": "Test Title"
                }
            ]
        }
        
        # Make request
        response = client.post("/api/v1/content-generate", json=request_data)
        
        # Verify response
        assert response.status_code == 400  # Bad request
        
        data = response.json()
        assert "detail" in data
        assert "Invalid content type" in data["detail"]
    
    @patch("app.ai.content_generate.routers.content_generate_router.tokenizer_service")
    def test_generate_content_token_limit_exceeded(self, mock_tokenizer_service):
        """Test error handling when token limit is exceeded"""
        # Mock tokenizer service to raise an error
        mock_tokenizer_service.validate_tokens.side_effect = Exception("Token limit exceeded")
        
        # Request data
        request_data = {
            "intent": "As a developer, I want to create a REST API.",
            "text_used": "Sample text." * 1000,  # Make it very long
            "content_types": [
                {
                    "type": "tutorial",
                    "title": "Test Title"
                }
            ]
        }
        
        # Make request
        response = client.post("/api/v1/content-generate", json=request_data)
        
        # Verify response
        assert response.status_code == 400  # Bad request
        
        data = response.json()
        assert "detail" in data 