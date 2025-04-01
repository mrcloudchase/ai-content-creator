import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from app.ai.core.services.ai_core_service import AIService, OpenAIServiceError
from app.ai.core.services.tokenizer_core_service import TokenizerService

@pytest.mark.asyncio
async def test_ai_tokenizer_integration():
    """Test the integration between AI and tokenizer services."""
    test_text = "This is a test prompt that will be tokenized and then sent to the AI service."
    
    # Count tokens
    token_result = TokenizerService.count_tokens(test_text)
    
    # Mock OpenAI completion
    with patch('app.ai.core.services.ai_core_service.AsyncOpenAI') as mock_openai:
        # Configure the mock
        mock_instance = mock_openai.return_value
        mock_instance.chat = MagicMock()
        mock_instance.chat.completions = MagicMock()
        mock_instance.chat.completions.create = AsyncMock()
        
        # Mock response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "This is a test response"
        mock_response.model = "gpt-3.5-turbo"
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = token_result["token_count"]
        mock_response.usage.completion_tokens = 5
        mock_response.usage.total_tokens = token_result["token_count"] + 5
        
        mock_instance.chat.completions.create.return_value = mock_response
        
        # Create AIService
        ai_service = AIService()
        
        # Generate completion with the tokenized text
        result = await ai_service.generate_completion(test_text)
        
        # Verify prompt was passed correctly
        mock_instance.chat.completions.create.assert_called_once()
        call_args = mock_instance.chat.completions.create.call_args[1]
        assert call_args["messages"][0]["content"] == test_text
        
        # Verify response processing
        assert result["text"] == "This is a test response"
        assert result["model"] == "gpt-3.5-turbo"
        assert result["usage"]["prompt_tokens"] == token_result["token_count"]
        assert result["usage"]["completion_tokens"] == 5
        assert result["usage"]["total_tokens"] == token_result["token_count"] + 5

@pytest.mark.asyncio
async def test_ai_service_error_handling():
    """Test error handling in the AI service."""
    # Mock OpenAI to raise an exception
    with patch('app.ai.core.services.ai_core_service.AsyncOpenAI') as mock_openai:
        # Configure the mock to raise an exception
        mock_instance = mock_openai.return_value
        mock_instance.chat = MagicMock()
        mock_instance.chat.completions = MagicMock()
        mock_instance.chat.completions.create = AsyncMock(side_effect=Exception("API error"))
        
        # Create AIService
        ai_service = AIService()
        
        # Try to generate completion and expect an error
        with pytest.raises(OpenAIServiceError):
            await ai_service.generate_completion("Test prompt") 