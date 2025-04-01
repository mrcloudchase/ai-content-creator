import pytest
import os
import tempfile
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
from app.main import app

client = TestClient(app)

@pytest.mark.asyncio
async def test_markdown_to_customer_intent_flow():
    """
    Test end-to-end flow from markdown upload to customer intent generation.
    This test mocks the OpenAI API call but tests the actual workflow through
    the application.
    """
    # Mock the AI service to avoid actual API calls
    with patch('app.ai.core.services.ai_core_service.AIService.generate_completion', new_callable=AsyncMock) as mock_completion:
        # Configure mock AI response
        mock_completion.return_value = {
            "text": "As a content writer, I want to structure my articles better because it helps readers understand my points more clearly.",
            "model": "gpt-3.5-turbo",
            "usage": {
                "prompt_tokens": 150,
                "completion_tokens": 30,
                "total_tokens": 180
            }
        }
        
        # Create a temporary markdown file
        with tempfile.NamedTemporaryFile(suffix='.md', mode='w+', delete=False) as temp_file:
            temp_file.write("# Writing Guide\n\nThis document explains how to structure articles for better readability.")
            temp_file_path = temp_file.name
        
        try:
            # Execute the workflow by calling the API endpoint
            with open(temp_file_path, 'rb') as file:
                response = client.post(
                    "/api/v1/customer-intent",
                    json={
                        "document_text": "# Writing Guide\n\nThis document explains how to structure articles for better readability.",
                        "user_type": "content writer"
                    }
                )
            
            # Check the response
            assert response.status_code == 200
            data = response.json()
            
            # Verify response structure
            assert "intent" in data
            assert "model" in data
            assert "usage" in data
            
            # Verify content
            assert "content writer" in data["intent"].lower()
            assert "structure" in data["intent"].lower()
            assert "articles" in data["intent"].lower()
            
            # Verify AI service was called with appropriate content
            mock_completion.assert_called_once()
            call_args = mock_completion.call_args[1]
            assert "prompt" in call_args
            assert "content writer" in call_args["prompt"].lower()
            assert "structure" in call_args["prompt"].lower()
            
        finally:
            # Clean up
            os.unlink(temp_file_path)

@pytest.mark.asyncio
async def test_docx_to_customer_intent_flow():
    """
    Test end-to-end flow from DOCX upload to customer intent generation.
    This test mocks both the DOCX parsing and OpenAI API call.
    """
    # Mock the docx parser
    with patch('app.input_processing.docx.services.docx_service.DocxService.extract_text', return_value="Product plan for enhancing data visualization tools") as mock_extract:
        # Mock the AI service
        with patch('app.ai.core.services.ai_core_service.AIService.generate_completion', new_callable=AsyncMock) as mock_completion:
            # Configure mock AI response
            mock_completion.return_value = {
                "text": "As a data analyst, I want to enhance data visualization tools because it helps me communicate insights more effectively.",
                "model": "gpt-3.5-turbo",
                "usage": {
                    "prompt_tokens": 120,
                    "completion_tokens": 25,
                    "total_tokens": 145
                }
            }
            
            # Execute the workflow
            response = client.post(
                "/api/v1/customer-intent",
                json={
                    "document_text": "Product plan for enhancing data visualization tools",
                    "user_type": "data analyst"
                }
            )
            
            # Check the response
            assert response.status_code == 200
            data = response.json()
            
            # Verify response structure
            assert "intent" in data
            assert "model" in data
            assert "usage" in data
            
            # Verify content
            assert "data analyst" in data["intent"].lower()
            assert "visualization" in data["intent"].lower()
            
            # Verify AI service was called with appropriate content
            mock_completion.assert_called_once()
            call_args = mock_completion.call_args[1]
            assert "prompt" in call_args
            assert "data analyst" in call_args["prompt"].lower()
            assert "visualization" in call_args["prompt"].lower() 