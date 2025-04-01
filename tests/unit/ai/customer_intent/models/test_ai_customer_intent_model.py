import pytest
from app.ai.customer_intent.models.ai_customer_intent_model import CustomerIntentRequest, CustomerIntentResponse
from unittest.mock import MagicMock
from fastapi import UploadFile


def test_customer_intent_request_validation():
    """Test the validation of CustomerIntentRequest model"""
    # Create a mock UploadFile
    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "test_document.md"
    
    # Valid request with file
    valid_request = CustomerIntentRequest(file=mock_file)
    
    # Assert that file is correctly set
    assert valid_request.file is not None
    assert valid_request.file.filename == "test_document.md"
    
    # Test with missing file
    with pytest.raises(Exception):
        CustomerIntentRequest()  # This should raise an error as file is required


def test_customer_intent_response_validation():
    """Test the validation of CustomerIntentResponse model"""
    # Valid response with all required fields
    valid_response = CustomerIntentResponse(
        intent="As a developer, I want to create an API to automate content creation because it will save time.",
        model="gpt-3.5-turbo",
        usage={
            "prompt_tokens": 50,
            "completion_tokens": 30,
            "total_tokens": 80
        }
    )
    
    assert valid_response.intent == "As a developer, I want to create an API to automate content creation because it will save time."
    assert valid_response.model == "gpt-3.5-turbo"
    assert valid_response.usage["prompt_tokens"] == 50
    assert valid_response.usage["completion_tokens"] == 30
    assert valid_response.usage["total_tokens"] == 80
    
    # Test serialization to dict
    response_dict = valid_response.model_dump()
    assert isinstance(response_dict, dict)
    assert "intent" in response_dict
    assert "model" in response_dict
    assert "usage" in response_dict 