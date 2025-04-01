import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import io

from app.ai.customer_intent.models.ai_customer_intent_model import CustomerIntentResponse
from app.ai.customer_intent.routers.ai_customer_intent_router import CustomerIntentRouterError


@pytest.mark.asyncio
async def test_customer_intent_endpoint_success(client, mock_markdown_upload, mock_openai_response):
    """Test successful customer intent generation via API endpoint"""
    # Mock all the services called by the router
    with patch("app.ai.customer_intent.routers.ai_customer_intent_router.file_handler_routing_service.validate_file_type", 
               return_value="markdown"), \
         patch("app.ai.customer_intent.routers.ai_customer_intent_router.markdown_service.extract_text", 
               return_value="Extracted markdown text"), \
         patch("app.ai.customer_intent.routers.ai_customer_intent_router.InputProcessingService.process_text", 
               return_value="Processed text"), \
         patch("app.ai.customer_intent.routers.ai_customer_intent_router.tokenizer_service.validate_tokens", 
               return_value={
                   "token_count": 100,
                   "model_limit": 4096,
                   "tokens_remaining": 3996,
                   "percentage_used": 2.44,
                   "model": "gpt-4-test",
                   "model_family": "gpt",
                   "capabilities": {"supports_functions": True, "supports_vision": False},
                   "encoding": "cl100k_base"
               }), \
         patch("app.ai.customer_intent.routers.ai_customer_intent_router.customer_intent_service.format_customer_intent_prompt", 
               return_value={
                   "messages": [
                       {"role": "system", "content": "You are an expert..."},
                       {"role": "user", "content": "Please analyze..."}
                   ]
               }), \
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
        
        # Create a test file to upload
        test_file = io.BytesIO(b"# Test Markdown\n\nThis is test content.")
        
        # Make the request
        response = client.post(
            "/api/v1/customer-intent",
            files={"file": ("test.md", test_file, "text/markdown")}
        )
        
        # Verify the response
        assert response.status_code == 200
        data = response.json()
        
        # Check that we got a valid response structure
        assert "intent" in data
        assert data["intent"] == "As a content creator, I want to streamline my workflow because it saves time and increases productivity."
        assert data["model"] == "gpt-4-test"
        assert data["model_family"] == "gpt"
        assert "usage" in data
        assert data["token_count"] == 100
        assert data["token_limit"] == 4096
        assert data["remaining_tokens"] == 3996
        
        # Verify the AI service was called with correct data
        mock_generate.assert_called_once()
        call_args = mock_generate.call_args[1]
        assert "messages" in call_args
        assert len(call_args["messages"]) == 2


@pytest.mark.asyncio
async def test_customer_intent_endpoint_invalid_file_type(client):
    """Test customer intent generation with invalid file type"""
    # Create a test file with unsupported extension
    test_file = io.BytesIO(b"This is test content")
    
    # Make the request
    response = client.post(
        "/api/v1/customer-intent",
        files={"file": ("test.pdf", test_file, "application/pdf")}
    )
    
    # Verify the response
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Unsupported file type" in data["detail"]


@pytest.mark.asyncio
async def test_customer_intent_endpoint_empty_file(client):
    """Test customer intent generation with empty file"""
    # Create an empty test file
    test_file = io.BytesIO(b"")
    
    # Make the request
    response = client.post(
        "/api/v1/customer-intent",
        files={"file": ("test.md", test_file, "text/markdown")}
    )
    
    # Verify the response
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "empty" in data["detail"].lower()


@pytest.mark.asyncio
async def test_customer_intent_endpoint_ai_service_error(client, mock_markdown_upload):
    """Test handling of AI service errors in the endpoint"""
    # Mock services but have AI service raise an error
    with patch("app.ai.customer_intent.routers.ai_customer_intent_router.file_handler_routing_service.validate_file_type",
               return_value="markdown"), \
         patch("app.ai.customer_intent.routers.ai_customer_intent_router.markdown_service.extract_text",
               return_value="Extracted markdown text"), \
         patch("app.ai.customer_intent.routers.ai_customer_intent_router.InputProcessingService.process_text",
               return_value="Processed text"), \
         patch("app.ai.customer_intent.routers.ai_customer_intent_router.tokenizer_service.validate_tokens",
               return_value={
                   "token_count": 100,
                   "model_limit": 4096,
                   "tokens_remaining": 3996,
                   "percentage_used": 2.44,
                   "model": "gpt-4-test",
                   "model_family": "gpt",
                   "capabilities": {"supports_functions": True, "supports_vision": False},
                   "encoding": "cl100k_base"
               }), \
         patch("app.ai.customer_intent.routers.ai_customer_intent_router.customer_intent_service.format_customer_intent_prompt",
               return_value={
                   "messages": [
                       {"role": "system", "content": "You are an expert..."},
                       {"role": "user", "content": "Please analyze..."}
                   ]
               }), \
         patch("app.ai.customer_intent.routers.ai_customer_intent_router.ai_service.generate_completion",
               new_callable=AsyncMock) as mock_generate, \
         patch("app.ai.customer_intent.routers.ai_customer_intent_router.generate_intent",
               side_effect=CustomerIntentRouterError("AI service error: API rate limit exceeded")):

        # Create a test file to upload
        test_file = io.BytesIO(b"# Test Markdown\n\nThis is test content.")

        # Make the request
        response = client.post(
            "/api/v1/customer-intent",
            files={"file": ("test.md", test_file, "text/markdown")}
        )

        # Verify the response
        assert response.status_code == 400  # Bad Request since we're raising CustomerIntentRouterError
        data = response.json()
        assert "detail" in data
        assert "AI service error" in data["detail"]
        assert "API rate limit" in data["detail"]
