import pytest
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
    """Test successful customer intent generation"""
    # Mock the OpenAI service response
    with patch('app.services.openai_service.OpenAIService.generate_completion', new_callable=AsyncMock) as mock_generate:
        # Configure the mock
        mock_result = {
            "text": "As a user, I want to create a secure account because I need to access personalized features while ensuring my data is protected.",
            "model": "gpt-3.5-turbo",
            "usage": {"prompt_tokens": 150, "completion_tokens": 25, "total_tokens": 175}
        }
        mock_generate.return_value = mock_result
        
        # Make request to the endpoint
        response = client.post(
            "/api/v1/customer-intent/generate",
            json={
                "document_text": SAMPLE_DOCUMENT,
                "max_tokens": 150,
                "temperature": 0.5
            }
        )
        
        # Assert response
        assert response.status_code == 200
        data = response.json()
        assert "intent" in data
        assert "model" in data
        assert "usage" in data
        assert "user" in data["intent"].lower()

def test_generate_customer_intent_with_user_type():
    """Test customer intent generation with specified user type"""
    # Mock the OpenAI service response
    with patch('app.services.openai_service.OpenAIService.generate_completion', new_callable=AsyncMock) as mock_generate:
        # Configure the mock
        mock_result = {
            "text": "As an admin, I want to manage user accounts because I need to maintain security and ensure proper access controls.",
            "model": "gpt-3.5-turbo",
            "usage": {"prompt_tokens": 160, "completion_tokens": 25, "total_tokens": 185}
        }
        mock_generate.return_value = mock_result
        
        # Make request to the endpoint
        response = client.post(
            "/api/v1/customer-intent/generate",
            json={
                "document_text": SAMPLE_DOCUMENT,
                "user_type": "admin",
                "max_tokens": 150,
                "temperature": 0.5
            }
        )
        
        # Assert response
        assert response.status_code == 200
        data = response.json()
        assert "admin" in data["intent"].lower()
        
        # Verify the mock was called with the user_type in the prompt
        called_args = mock_generate.call_args[1]
        assert "admin" in called_args["prompt"]

def test_generate_customer_intent_service_error():
    """Test handling of service errors"""
    # Mock the OpenAI service to raise an exception
    with patch('app.services.openai_service.OpenAIService.generate_completion', new_callable=AsyncMock) as mock_generate:
        # Configure the mock to raise an exception
        mock_generate.side_effect = Exception("Test service error")
        
        # Make request to the endpoint
        response = client.post(
            "/api/v1/customer-intent/generate",
            json={
                "document_text": SAMPLE_DOCUMENT,
                "max_tokens": 150,
                "temperature": 0.5
            }
        )
        
        # Assert response
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "error" in data["detail"].lower() 