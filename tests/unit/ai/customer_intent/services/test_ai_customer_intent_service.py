import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.ai.customer_intent.services.ai_customer_intent_service import CustomerIntentService
from app.ai.core.services.ai_core_service import AIService

def test_format_customer_intent_prompt():
    """Test formatting customer intent prompt."""
    # Create service instance
    ai_service = MagicMock(spec=AIService)
    service = CustomerIntentService(ai_service)
    
    # Test with no user type
    document_text = "This is a sample document."
    prompt = service.format_customer_intent_prompt(document_text)
    
    # Verify prompt structure
    assert "Write a customer intent in the following format:" in prompt
    assert "As a <type of user>, I want to do <what> because <why>" in prompt
    assert document_text in prompt
    
    # Test with specific user type
    prompt = service.format_customer_intent_prompt(document_text, user_type="developer")
    
    # Verify user type is included
    assert "Write a customer intent for a developer" in prompt
    assert "As a developer" in prompt
    assert document_text in prompt

@pytest.mark.asyncio
async def test_generate_customer_intent():
    """Test generating customer intent."""
    # Create mock AIService
    ai_service = MagicMock(spec=AIService)
    
    # Configure generate_completion mock
    ai_service.generate_completion = AsyncMock()
    ai_service.generate_completion.return_value = {
        "text": "As a user, I want to create reports because I need to analyze data.",
        "model": "gpt-3.5-turbo",
        "usage": {
            "prompt_tokens": 50,
            "completion_tokens": 20,
            "total_tokens": 70
        }
    }
    
    # Create service instance
    service = CustomerIntentService(ai_service)
    
    # Test without user type
    document_text = "Feature request: Generate PDF reports from data."
    result = await service.generate_customer_intent(document_text)
    
    # Verify result structure
    assert "intent" in result
    assert "model" in result
    assert "usage" in result
    assert "As a user" in result["intent"]
    assert "reports" in result["intent"]
    assert "model" in result
    assert result["model"] == "gpt-3.5-turbo"
    assert "usage" in result
    assert "prompt_tokens" in result["usage"]
    
    # Verify generate_completion was called with correct parameters
    ai_service.generate_completion.assert_called_once()
    call_args = ai_service.generate_completion.call_args[1]
    assert "prompt" in call_args
    assert document_text in call_args["prompt"]
    assert call_args["max_tokens"] == 150
    assert call_args["temperature"] == 0.5
    
    # Reset mock
    ai_service.generate_completion.reset_mock()
    
    # Test with specific user type and custom parameters
    result = await service.generate_customer_intent(
        document_text="Feature request: Export data to Excel.",
        user_type="data analyst",
        max_tokens=200,
        temperature=0.7
    )
    
    # Verify generate_completion was called with correct parameters
    ai_service.generate_completion.assert_called_once()
    call_args = ai_service.generate_completion.call_args[1]
    assert "data analyst" in call_args["prompt"]
    assert "Export data to Excel" in call_args["prompt"]
    assert call_args["max_tokens"] == 200
    assert call_args["temperature"] == 0.7 