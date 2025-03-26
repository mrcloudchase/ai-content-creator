import pytest
from fastapi.testclient import TestClient
import io
import json
import os
from unittest.mock import patch, MagicMock
from app.main import app
from docx import Document
from app.routers import ai
from app.services.openai_service import OpenAIService

client = TestClient(app)

def create_test_document(content):
    """Create a test document with the given content"""
    doc = Document()
    doc.add_paragraph(content)
    
    # Save the document to a bytesIO object
    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    
    return file_stream

# Store the original generate_completion method
original_generate_completion = OpenAIService.generate_completion

@pytest.fixture
def mock_openai():
    """Fixture to mock the OpenAI service"""
    async def mock_generate_completion(*args, **kwargs):
        return {
            "text": "This is a mock response from OpenAI.",
            "model": "gpt-3.5-turbo",
            "usage": {
                "prompt_tokens": 20,
                "completion_tokens": 10,
                "total_tokens": 30
            }
        }
    
    # Apply the patch
    OpenAIService.generate_completion = mock_generate_completion
    
    yield
    
    # Restore the original method
    OpenAIService.generate_completion = original_generate_completion

@pytest.mark.asyncio
async def test_document_parser_to_ai_workflow(mock_openai):
    """Test the workflow of parsing a document and feeding it to the AI endpoint"""
    # Create a test document
    content = "This is a test document that will be parsed and then sent to the AI endpoint."
    docx_file = create_test_document(content)
    
    # Step 1: Parse the document
    parse_response = client.post(
        "/api/v1/documents/extract-text",
        files={"file": ("test.docx", docx_file, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    )
    
    # Check if parsing was successful
    assert parse_response.status_code == 200
    parsed_text = parse_response.text
    
    # Step 2: Send the parsed text to the AI endpoint
    ai_response = client.post(
        "/api/v1/tokens/count",
        json={"text": parsed_text}
    )
    
    # Check if token counting was successful
    assert ai_response.status_code == 200
    token_data = ai_response.json()
    assert token_data["token_count"] > 0
    
    # Step 3: Send the parsed text to the AI endpoint
    ai_response = client.post(
        "/api/v1/ai/completions",
        json={"prompt": parsed_text}
    )
    
    # Check if AI response was successful
    assert ai_response.status_code == 200
    ai_data = ai_response.json()
    assert "text" in ai_data
    assert "usage" in ai_data
    assert isinstance(ai_data["text"], str) and len(ai_data["text"]) > 0

@pytest.mark.asyncio
async def test_document_with_special_chars(mock_openai):
    """Test handling a document with special characters"""
    # Create a test document with special characters
    content = 'Document with special characters: quotes "like this" and unicode chars like é, ñ, ü.'
    docx_file = create_test_document(content)
    
    # Step 1: Parse the document
    parse_response = client.post(
        "/api/v1/documents/extract-text",
        files={"file": ("test.docx", docx_file, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    )
    
    # Check if parsing was successful
    assert parse_response.status_code == 200
    parsed_text = parse_response.text
    
    # Step 2: Send the parsed text to the AI endpoint
    ai_response = client.post(
        "/api/v1/ai/completions",
        json={"prompt": parsed_text}
    )
    
    # Check if AI response was successful
    assert ai_response.status_code == 200 