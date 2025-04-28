import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestContentWorkflow:
    """End-to-end tests for the content generation workflow"""
    
    @patch("app.ai.customer_intent.routers.ai_customer_intent_router.ai_service")
    @patch("app.ai.content_types.routers.content_type_router.ai_service")
    @patch("app.ai.content_generate.routers.content_generate_router.ai_service")
    @patch("app.ai.content_generate.routers.content_generate_router.tokenizer_service")
    @patch("app.ai.content_types.routers.content_type_router.tokenizer_service")
    @patch("app.ai.customer_intent.routers.ai_customer_intent_router.tokenizer_service")
    @patch("app.ai.customer_intent.routers.ai_customer_intent_router.extract_file_content")
    def test_complete_workflow(
        self,
        mock_extract_file_content,
        mock_customer_intent_tokenizer,
        mock_content_types_tokenizer,
        mock_content_generate_tokenizer,
        mock_content_generate_ai,
        mock_content_types_ai,
        mock_customer_intent_ai
    ):
        """Test the complete workflow from intent to content generation"""
        # 1. Mock file extraction for customer intent
        mock_extract_file_content.return_value = "This is sample document text about REST APIs."
        
        # 2. Mock token validation for all services
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
        mock_customer_intent_tokenizer.validate_tokens.return_value = mock_token_info
        mock_content_types_tokenizer.validate_tokens.return_value = mock_token_info
        mock_content_generate_tokenizer.validate_tokens.return_value = mock_token_info
        
        # 3. Mock AI service responses
        # Customer intent generation
        customer_intent_response = {
            "text": "As a developer, I want to create a REST API because it will help me serve data to clients.",
            "model": "gpt-4",
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150
            }
        }
        mock_customer_intent_ai.generate_completion = AsyncMock(return_value=customer_intent_response)
        
        # Content type selection
        content_types_response = {
            "text": '{"content_types": [{"type": "tutorial", "confidence": 85, "reasoning": "The intent focuses on learning how to create a REST API."}]}',
            "model": "gpt-4",
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150
            }
        }
        mock_content_types_ai.generate_completion = AsyncMock(return_value=content_types_response)
        
        # Content generation
        content_generation_response = {
            "text": "# Building a REST API with FastAPI\n\nThis tutorial will walk you through creating a REST API with FastAPI.",
            "model": "gpt-4",
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150
            }
        }
        mock_content_generate_ai.generate_completion = AsyncMock(return_value=content_generation_response)
        
        # STEP 1: Call customer intent endpoint to generate intent from document
        # Create a test file in memory
        test_file = {
            "file": ("test.txt", b"This is sample document text about REST APIs.")
        }
        
        # Call the endpoint to generate customer intent
        intent_response = client.post("/api/v1/customer-intent", files=test_file)
        assert intent_response.status_code == 200
        
        intent_data = intent_response.json()
        assert "intent" in intent_data
        assert "text_used" in intent_data
        
        # Get the generated intent and text
        intent = intent_data["intent"]
        text = intent_data["text_used"]
        
        # STEP 2: Call content types endpoint to select content types
        content_types_request = {
            "intent": intent,
            "text_used": text
        }
        
        # Call the endpoint to select content types
        content_types_response = client.post("/api/v1/content-types", json=content_types_request)
        assert content_types_response.status_code == 200
        
        content_types_data = content_types_response.json()
        assert "selected_types" in content_types_data
        assert len(content_types_data["selected_types"]) > 0
        
        # Extract the first selected content type
        selected_type = content_types_data["selected_types"][0]["type"]
        
        # STEP 3: Call content generate endpoint to create content
        content_generate_request = {
            "intent": intent,
            "text_used": text,
            "content_types": [
                {
                    "type": selected_type,
                    "title": "Building a REST API"
                }
            ]
        }
        
        # Call the endpoint to generate content
        content_generate_response = client.post("/api/v1/content-generate", json=content_generate_request)
        assert content_generate_response.status_code == 200
        
        content_generate_data = content_generate_response.json()
        assert "generated_content" in content_generate_data
        assert len(content_generate_data["generated_content"]) == 1
        
        # Verify the generated content matches the requested type
        assert content_generate_data["generated_content"][0]["type"] == selected_type
        assert content_generate_data["generated_content"][0]["title"] == "Building a REST API"
        assert "Building a REST API with FastAPI" in content_generate_data["generated_content"][0]["content"] 