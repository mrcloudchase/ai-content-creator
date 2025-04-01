import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import os
import openai

from app.ai.core.services.ai_core_service import AIService, OpenAIServiceError


class TestAIService:
    """Tests for the AIService class"""

    def test_init_with_settings(self, openai_settings):
        """Test initialization with settings"""
        with patch("app.ai.core.services.ai_core_service.openai.AsyncOpenAI") as mock_openai:
            service = AIService(openai_settings)
            assert service.settings == openai_settings
            mock_openai.assert_called_once()

    def test_init_with_env_vars(self):
        """Test initialization with environment variables"""
        with patch("app.ai.core.services.ai_core_service.openai.AsyncOpenAI") as mock_openai:
            # Save original env var
            original_api_key = os.environ.get("OPENAI_API_KEY")
            
            try:
                # Set test env var
                os.environ["OPENAI_API_KEY"] = "test-env-api-key"
                
                # Create service without settings
                service = AIService(None)
                
                # Verify client was created with env var
                mock_openai.assert_called_once()
                # Check if API key was obtained from env
                call_args = mock_openai.call_args[1]
                assert call_args["api_key"] == "test-env-api-key"
                
            finally:
                # Restore original env var
                if original_api_key:
                    os.environ["OPENAI_API_KEY"] = original_api_key
                else:
                    del os.environ["OPENAI_API_KEY"]

    @pytest.mark.asyncio
    async def test_generate_completion_success(self, mock_openai_response):
        """Test successful completion generation"""
        # Setup
        with patch("app.ai.core.services.ai_core_service.openai.AsyncOpenAI") as mock_openai:
            # Setup the mock client
            mock_client = MagicMock()
            mock_client.chat.completions.create = AsyncMock(return_value=mock_openai_response)
            mock_openai.return_value = mock_client
            
            # Create test service
            service = AIService(MagicMock())
            service.client = mock_client
            
            # Test data
            messages = [
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": "Write a customer intent statement"}
            ]
            
            # Call method
            result = await service.generate_completion(messages=messages)
            
            # Assert response was processed correctly
            assert "text" in result
            assert result["text"] == "As a content creator, I want to streamline my workflow because it saves time and increases productivity."
            assert result["model"] == "gpt-4-test"
            assert "usage" in result
            assert result["usage"]["prompt_tokens"] == 100
            assert result["usage"]["completion_tokens"] == 50
            assert result["usage"]["total_tokens"] == 150
            
            # Assert OpenAI API was called with correct parameters
            mock_client.chat.completions.create.assert_called_once()
            call_args = mock_client.chat.completions.create.call_args[1]
            assert call_args["messages"] == messages

    @pytest.mark.asyncio
    async def test_generate_completion_with_model_param(self, mock_openai_response):
        """Test completion generation with model parameter"""
        # Setup
        with patch("app.ai.core.services.ai_core_service.openai.AsyncOpenAI") as mock_openai:
            # Setup the mock client
            mock_client = MagicMock()
            mock_client.chat.completions.create = AsyncMock(return_value=mock_openai_response)
            mock_openai.return_value = mock_client
            
            # Create test service
            service = AIService(MagicMock())
            service.client = mock_client
            
            # Test data
            messages = [{"role": "user", "content": "Test"}]
            model = "gpt-3.5-turbo-test"
            
            # Call method
            await service.generate_completion(messages=messages, model=model)
            
            # Assert model parameter was used
            call_args = mock_client.chat.completions.create.call_args[1]
            assert call_args["model"] == "gpt-3.5-turbo-test"

    @pytest.mark.asyncio
    async def test_generate_completion_error_handling(self):
        """Test error handling in completion generation"""
        # Setup
        with patch("app.ai.core.services.ai_core_service.openai.AsyncOpenAI") as mock_openai:
            # Setup client to raise an exception
            mock_client = MagicMock()
            mock_client.chat.completions.create = AsyncMock(side_effect=Exception("API error"))
            mock_openai.return_value = mock_client
            
            # Create test service
            service = AIService(MagicMock())
            service.client = mock_client
            
            # Call method and check exception
            with pytest.raises(OpenAIServiceError) as excinfo:
                await service.generate_completion(messages=[{"role": "user", "content": "Test"}])
            
            # Verify error message
            assert "Error calling OpenAI API" in str(excinfo.value)
            assert "API error" in str(excinfo.value)
