import pytest
from unittest.mock import patch, AsyncMock
import io
from fastapi.testclient import TestClient
import os

from app.main import app
from app.ai.core.services.ai_core_service import OpenAIServiceError
from app.ai.customer_intent.routers.ai_customer_intent_router import CustomerIntentRouterError


class TestEndToEndFlow:
    """End-to-end tests for the complete API flow"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_markdown_flow(self, client, mock_openai_response):
        """Test end-to-end flow with a markdown file"""
        # Mock all required services to avoid actual API calls
        with patch("app.ai.customer_intent.routers.ai_customer_intent_router.markdown_service.extract_text", 
                  return_value="# Test Document\n\nThis is extracted content from a markdown file."), \
             patch("app.ai.customer_intent.routers.ai_customer_intent_router.ai_service.generate_completion", 
                  new_callable=AsyncMock) as mock_generate:
            
            # Configure the mock AI service response
            mock_generate.return_value = {
                "text": "As a content creator, I want to streamline my workflow because it saves time and increases productivity.",
                "model": "gpt-4-test",
                "usage": {
                    "prompt_tokens": 100,
                    "completion_tokens": 50,
                    "total_tokens": 150
                }
            }
            
            # Create a test markdown file
            file_content = """# Test Markdown Document
            
## Introduction
This is a test document for our AI content creator.

## Customer Needs
- Need to simplify workflow
- Need to save time
- Need to improve productivity
            """
            test_file = io.BytesIO(file_content.encode("utf-8"))
            
            # Make an API request
            response = client.post(
                "/api/v1/customer-intent",
                files={"file": ("test_document.md", test_file, "text/markdown")}
            )
            
            # Verify response
            assert response.status_code == 200
            data = response.json()
            
            # Check response structure
            assert "intent" in data
            assert data["intent"] == "As a content creator, I want to streamline my workflow because it saves time and increases productivity."
            assert data["model"] == "gpt-4-test"
            assert data["model_family"] is not None
            assert "usage" in data
            assert "token_count" in data
            assert "token_limit" in data
            assert "remaining_tokens" in data
            
            # Verify AI service was called
            mock_generate.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_end_to_end_txt_flow(self, client, mock_openai_response):
        """Test end-to-end flow with a text file"""
        # Mock all required services to avoid actual API calls
        with patch("app.ai.customer_intent.routers.ai_customer_intent_router.txt_service.extract_text", 
                  return_value="This is extracted content from a text file."), \
             patch("app.ai.customer_intent.routers.ai_customer_intent_router.ai_service.generate_completion", 
                  new_callable=AsyncMock) as mock_generate:
            
            # Configure the mock AI service response
            mock_generate.return_value = {
                "text": "As a business owner, I want to automate repetitive tasks because it reduces errors and frees up time for strategic work.",
                "model": "gpt-4-test",
                "usage": {
                    "prompt_tokens": 80,
                    "completion_tokens": 60,
                    "total_tokens": 140
                }
            }
            
            # Create a test text file
            file_content = """Test Text Document
            
Introduction
This is a test document for our AI content creator.

Customer Needs
The business owner needs to automate repetitive tasks to reduce errors and free up time.
            """
            test_file = io.BytesIO(file_content.encode("utf-8"))
            
            # Make an API request
            response = client.post(
                "/api/v1/customer-intent",
                files={"file": ("test_document.txt", test_file, "text/plain")}
            )
            
            # Verify response
            assert response.status_code == 200
            data = response.json()
            
            # Check response structure
            assert "intent" in data
            assert data["intent"] == "As a business owner, I want to automate repetitive tasks because it reduces errors and frees up time for strategic work."
            assert data["model"] == "gpt-4-test"
            
            # Verify AI service was called
            mock_generate.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_end_to_end_error_handling(self, client, mock_openai_response):
        """Test end-to-end error handling"""
        # Mock all required services but have the API raise CustomerIntentRouterError
        with patch("app.ai.customer_intent.routers.ai_customer_intent_router.markdown_service.extract_text",
                  return_value="This is extracted content."), \
             patch("app.ai.customer_intent.routers.ai_customer_intent_router.generate_intent", 
                  side_effect=CustomerIntentRouterError("AI service error: API quota exceeded")):

            # Create a test file
            file_content = "# Test Error Document"
            test_file = io.BytesIO(file_content.encode("utf-8"))

            # Make an API request
            response = client.post(
                "/api/v1/customer-intent",
                files={"file": ("test_error.md", test_file, "text/markdown")}
            )

            # Verify error response
            assert response.status_code == 400  # Bad Request since we're raising CustomerIntentRouterError
            data = response.json()
            assert "detail" in data
            assert "AI service error" in data["detail"]
            assert "API quota" in data["detail"]
    
    def test_api_health_endpoint(self, client):
        """Test the API health endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
        assert "version" in data
    
    def test_api_root_endpoint(self, client):
        """Test the API root endpoint"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "documentation" in data
        assert "endpoints" in data
        assert "customer_intent" in data["endpoints"]
    
    def test_api_docs_endpoint(self, client):
        """Test the API documentation endpoint"""
        response = client.get("/docs")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
