import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import os
from app.services.openai_service import OpenAIService, OpenAIServiceError
from app.config.settings import OpenAISettings
from dotenv import load_dotenv

# Load environment variables for testing
load_dotenv()

@pytest.mark.asyncio
async def test_generate_completion():
    """Test successful completion generation"""
    # Create a mock response
    mock_choice = MagicMock()
    mock_choice.message.content = "This is a test response"
    
    mock_usage = MagicMock()
    mock_usage.prompt_tokens = 10
    mock_usage.completion_tokens = 20
    mock_usage.total_tokens = 30
    
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_response.usage = mock_usage
    mock_response.model = "gpt-3.5-turbo"
    
    # Create a proper patch that completely replaces the AsyncOpenAI functionality
    with patch('app.services.openai_service.AsyncOpenAI', autospec=True) as mock_openai:
        # Set up the mock structure to match the AsyncOpenAI class structure
        mock_instance = mock_openai.return_value
        mock_instance.chat = MagicMock()
        mock_instance.chat.completions = MagicMock()
        mock_instance.chat.completions.create = AsyncMock(return_value=mock_response)
        
        # Use the actual settings from .env
        service = OpenAIService()
        result = await service.generate_completion("Test prompt")
        
        # Check response was processed correctly
        assert result["text"] == "This is a test response"
        assert result["model"] == "gpt-3.5-turbo"
        assert result["usage"]["prompt_tokens"] == 10
        assert result["usage"]["completion_tokens"] == 20
        assert result["usage"]["total_tokens"] == 30
        
        # Verify the call was made properly
        create_call = mock_instance.chat.completions.create
        create_call.assert_called_once()
        kwargs = create_call.call_args.kwargs
        assert kwargs["messages"][0]["content"] == "Test prompt"
        assert kwargs["model"] == service.settings.default_model

@pytest.mark.asyncio
async def test_generate_completion_with_params():
    """Test completion with custom parameters"""
    # Create a mock response
    mock_choice = MagicMock()
    mock_choice.message.content = "This is a test response with custom params"
    
    mock_usage = MagicMock()
    mock_usage.prompt_tokens = 15
    mock_usage.completion_tokens = 25
    mock_usage.total_tokens = 40
    
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_response.usage = mock_usage
    mock_response.model = "gpt-4"
    
    # Create a proper patch that completely replaces the AsyncOpenAI functionality
    with patch('app.services.openai_service.AsyncOpenAI', autospec=True) as mock_openai:
        # Set up the mock structure to match the AsyncOpenAI class structure
        mock_instance = mock_openai.return_value
        mock_instance.chat = MagicMock()
        mock_instance.chat.completions = MagicMock()
        mock_instance.chat.completions.create = AsyncMock(return_value=mock_response)
        
        # Use the actual settings from .env
        service = OpenAIService()
        
        # Test with custom parameters
        result = await service.generate_completion(
            "Test prompt with custom params",
            model="gpt-4",
            max_tokens=100,
            temperature=0.5
        )
        
        # Check response was processed correctly
        assert result["text"] == "This is a test response with custom params"
        assert result["model"] == "gpt-4"
        
        # Verify custom parameters were passed correctly
        create_call = mock_instance.chat.completions.create
        create_call.assert_called_once()
        kwargs = create_call.call_args.kwargs
        assert kwargs["model"] == "gpt-4"
        assert kwargs["max_tokens"] == 100
        assert kwargs["temperature"] == 0.5

@pytest.mark.asyncio
async def test_empty_prompt():
    """Test with empty prompt should raise assertion error"""
    # Use real settings from .env for consistent testing
    service = OpenAIService()
    with pytest.raises(AssertionError, match="Prompt cannot be empty"):
        await service.generate_completion("")

@pytest.mark.asyncio
async def test_api_error():
    """Test handling of API errors"""
    # Create a proper patch that completely replaces the AsyncOpenAI functionality
    with patch('app.services.openai_service.AsyncOpenAI', autospec=True) as mock_openai:
        # Set up the mock structure to match the AsyncOpenAI class structure
        mock_instance = mock_openai.return_value
        mock_instance.chat = MagicMock()
        mock_instance.chat.completions = MagicMock()
        mock_instance.chat.completions.create = AsyncMock(side_effect=Exception("API error"))
        
        # Use the actual settings from .env
        service = OpenAIService()
        
        # Test error handling
        with pytest.raises(OpenAIServiceError, match="Error calling OpenAI API"):
            await service.generate_completion("Test prompt") 