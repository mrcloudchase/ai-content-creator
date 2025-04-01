import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from app.ai.customer_intent.services.ai_customer_intent_service import CustomerIntentService
from app.ai.core.services.ai_core_service import AIService
from app.ai.customer_intent.models.ai_customer_intent_model import CustomerIntentRequest, CustomerIntentResponse

@pytest.mark.asyncio
async def test_customer_intent_workflow():
    """Test the customer intent service workflow from request to response."""
    # Mock AIService and its generate_completion method
    ai_service = MagicMock(spec=AIService)
    ai_service.generate_completion = AsyncMock()
    ai_service.generate_completion.return_value = {
        "text": "As a user, I want to create a dashboard to visualize data because it helps me understand trends quickly.",
        "model": "gpt-3.5-turbo",
        "usage": {
            "prompt_tokens": 40,
            "completion_tokens": 20,
            "total_tokens": 60
        }
    }
    
    # Create CustomerIntentService with mocked AIService
    service = CustomerIntentService(ai_service)
    
    # Create a request
    request = CustomerIntentRequest(
        document_text="Feature request for data visualization dashboard with charts and filters.",
        user_type="data analyst",
        max_tokens=150,
        temperature=0.7
    )
    
    # Process the request through the workflow
    result = await service.generate_customer_intent(
        document_text=request.document_text,
        user_type=request.user_type,
        max_tokens=request.max_tokens,
        temperature=request.temperature
    )
    
    # Verify the workflow steps
    ai_service.generate_completion.assert_called_once()
    
    # Check that input was processed correctly
    call_args = ai_service.generate_completion.call_args[1]
    assert "data analyst" in call_args["prompt"]
    assert "dashboard" in call_args["prompt"]
    assert call_args["max_tokens"] == 150
    assert call_args["temperature"] == 0.7
    
    # Check output format
    assert "intent" in result
    assert "model" in result
    assert "usage" in result
    assert "dashboard" in result["intent"]
    assert result["model"] == "gpt-3.5-turbo"

@pytest.mark.asyncio
async def test_customer_intent_workflow_error_handling():
    """Test error handling in the customer intent workflow."""
    # Mock AIService that raises an exception
    ai_service = MagicMock(spec=AIService)
    ai_service.generate_completion = AsyncMock(side_effect=Exception("Test error"))
    
    # Create CustomerIntentService with mocked AIService
    service = CustomerIntentService(ai_service)
    
    # Create a request
    request = CustomerIntentRequest(
        document_text="Feature request for data visualization."
    )
    
    # Process the request and expect an exception
    with pytest.raises(Exception):
        await service.generate_customer_intent(
            document_text=request.document_text
        )
    
    # Verify the workflow called the AI service
    ai_service.generate_completion.assert_called_once() 