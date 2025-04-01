import pytest
import io
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app

client = TestClient(app)

# Sample document text for testing
SAMPLE_DOCUMENT = """
Product Requirements Document
Feature: User Authentication System

1. Overview
This PRD outlines the requirements for implementing a secure user authentication system
for our web application. The system will support email/password login, social auth, and 2FA.

2. User Stories
- As a user, I want to create an account so I can access personalized features
- As a user, I want to reset my password if I forget it
- As an admin, I want to manage user accounts to maintain security
"""

def test_generate_customer_intent_success():
    """Test successful customer intent generation with file upload."""
    # Mock the AI service response
    with patch('app.ai.core.services.ai_core_service.AIService.generate_completion', new_callable=AsyncMock) as mock_generate:
        # Configure the mock
        mock_result = {
            "text": "As a user, I want to create a secure account because I need to access personalized features while ensuring my data is protected.",
            "model": "gpt-3.5-turbo",
            "usage": {"prompt_tokens": 150, "completion_tokens": 25, "total_tokens": 175}
        }
        mock_generate.return_value = mock_result
        
        # Create file-like object for upload
        file_content = io.BytesIO(SAMPLE_DOCUMENT.encode())
        
        # Make request to the endpoint with file upload
        response = client.post(
            "/api/v1/customer-intent",
            files={"file": ("test_document.md", file_content, "text/markdown")}
        )
        
        # Assert response
        assert response.status_code == 200
        data = response.json()
        assert "intent" in data
        assert "model" in data
        assert "usage" in data
        assert "user" in data["intent"].lower()

def test_generate_customer_intent_with_docx_file():
    """Test customer intent generation with DOCX file upload."""
    # Mock the AI service response
    with patch('app.ai.core.services.ai_core_service.AIService.generate_completion', new_callable=AsyncMock) as mock_generate, \
         patch('app.input_processing.docx.services.docx_service.DocxService.extract_text') as mock_extract:
        
        # Configure the mocks
        mock_result = {
            "text": "As a user, I want to manage my account because I need to maintain security and ensure proper access.",
            "model": "gpt-3.5-turbo",
            "usage": {"prompt_tokens": 160, "completion_tokens": 25, "total_tokens": 185}
        }
        mock_generate.return_value = mock_result
        mock_extract.return_value = SAMPLE_DOCUMENT
        
        # Create a dummy file content (not real docx, but sufficient for testing)
        file_content = io.BytesIO(b"dummy docx content")
        
        # Make request to the endpoint with file upload
        response = client.post(
            "/api/v1/customer-intent",
            files={"file": ("test_document.docx", file_content, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        )
        
        # Assert response
        assert response.status_code == 200
        data = response.json()
        assert "intent" in data
        assert "model" in data
        assert "usage" in data

def test_generate_customer_intent_service_error():
    """Test handling of service errors with file upload."""
    # Mock the AI service to raise an exception
    with patch('app.ai.core.services.ai_core_service.AIService.generate_completion', new_callable=AsyncMock) as mock_generate:
        # Configure the mock to raise an exception
        mock_generate.side_effect = Exception("Test service error")
        
        # Create file-like object for upload
        file_content = io.BytesIO(SAMPLE_DOCUMENT.encode())
        
        # Make request to the endpoint with file upload
        response = client.post(
            "/api/v1/customer-intent",
            files={"file": ("test_document.txt", file_content, "text/plain")}
        )
        
        # Assert response
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "error" in data["detail"].lower()

def test_generate_customer_intent_missing_file():
    """Test error handling when no file is provided."""
    # Make request to the endpoint without a file
    response = client.post("/api/v1/customer-intent")
    
    # Assert response
    assert response.status_code == 422  # Unprocessable Entity
    data = response.json()
    assert "detail" in data
    # Should have validation error about missing required field 