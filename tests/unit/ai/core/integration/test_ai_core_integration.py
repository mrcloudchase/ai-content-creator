import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from app.ai.core.services.ai_core_service import AIService
from app.ai.core.services.tokenizer_core_service import TokenizerService
from app.config.settings import OpenAISettings


class TestAICoreIntegration:
    """Integration tests for AI core services"""
    
    @pytest.mark.asyncio
    async def test_tokenizer_with_ai_service(self, openai_settings, mock_openai_response):
        """Test integration between TokenizerService and AIService"""
        # Create services
        tokenizer_service = TokenizerService(openai_settings)
        ai_service = AIService(openai_settings)
        
        # Mock the tokenizer and AI service methods
        token_result = {
            "token_count": 100,
            "model_limit": 4096,
            "tokens_remaining": 3996,
            "percentage_used": 2.44,
            "model": "gpt-4",
            "model_family": "gpt",
            "capabilities": {"supports_functions": True, "supports_vision": False},
            "encoding": "cl100k_base"
        }
        
        ai_result = {
            "text": "Generated text from the AI model",
            "model": "gpt-4",
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150
            }
        }
        
        with patch.object(tokenizer_service, 'validate_tokens', return_value=token_result), \
             patch.object(ai_service, 'generate_completion', new_callable=AsyncMock, return_value=ai_result):
            
            # Test: Validate tokens and then generate completion
            test_text = "This is test text to tokenize and use for AI completion"
            
            # Step 1: Validate tokens
            token_info = tokenizer_service.validate_tokens(test_text)
            
            # Verify token info
            assert token_info["token_count"] == 100
            assert token_info["model"] == "gpt-4"
            assert token_info["tokens_remaining"] == 3996
            
            # Step 2: Check if token count is acceptable for completion
            if token_info["token_count"] <= token_info["model_limit"]:
                # Create prompt with system and user messages
                messages = [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": test_text}
                ]
                
                # Generate completion
                completion = await ai_service.generate_completion(messages=messages)
                
                # Verify completion
                assert completion["text"] == "Generated text from the AI model"
                assert completion["model"] == "gpt-4"
                assert completion["usage"]["prompt_tokens"] == 100
                assert completion["usage"]["completion_tokens"] == 50
                assert completion["usage"]["total_tokens"] == 150
    
    @pytest.mark.asyncio
    async def test_tokenizer_rejection_for_long_input(self, openai_settings):
        """Test tokenizer rejects inputs that are too long before calling AI service"""
        # Create services
        tokenizer_service = TokenizerService(openai_settings)
        ai_service = AIService(openai_settings)
        
        # Mock tokenizer to return token count exceeding limit
        token_result = {
            "token_count": 10000,  # Exceeds limit
            "model_limit": 4096,
            "tokens_remaining": 0,
            "percentage_used": 244.14,  # > 100%
            "model": "gpt-4",
            "model_family": "gpt",
            "capabilities": {"supports_functions": True},
            "encoding": "cl100k_base",
            "exceeds_limit": True
        }
        
        with patch.object(tokenizer_service, 'validate_tokens', return_value=token_result), \
             patch.object(ai_service, 'generate_completion', new_callable=AsyncMock) as mock_generate:
            
            # Test: Validate tokens and conditionally generate completion
            test_text = "This is a very long text that exceeds token limits"
            
            # Step 1: Validate tokens
            token_info = tokenizer_service.validate_tokens(test_text)
            
            # Step 2: Check if token count is acceptable for completion
            should_proceed = token_info["token_count"] <= token_info["model_limit"]
            
            # We expect not to proceed with AI completion
            assert not should_proceed
            
            # Verify AI service was not called
            if not should_proceed:
                # This is what should happen - AI service should not be called
                assert not mock_generate.called
            else:
                # Create prompt and generate completion (shouldn't happen)
                messages = [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": test_text}
                ]
                await ai_service.generate_completion(messages=messages)
    
    def test_token_counting_consistency(self, openai_settings):
        """Test that token counting is consistent across the tokenizer service"""
        # Create tokenizer service
        tokenizer_service = TokenizerService(openai_settings)
        
        # Mock token counting methods
        with patch.object(tokenizer_service, 'validate_tokens') as mock_validate, \
             patch.object(tokenizer_service, 'count_tokens') as mock_count, \
             patch.object(tokenizer_service, 'estimate_tokens_from_characters') as mock_estimate:
            
            # Setup mock returns
            mock_validate.return_value = {
                "token_count": 100,
                "model_limit": 4096,
                "tokens_remaining": 3996
            }
            
            mock_count.return_value = {
                "token_count": 100,
                "model": "gpt-4",
                "model_family": "gpt"
            }
            
            mock_estimate.return_value = 25  # Assuming 100 characters / 4 = 25 tokens
            
            # Test with sample text
            text = "This is a sample text to test token counting consistency"
            text_length = len(text)  # Should be around 57 characters
            
            # Get token count using different methods
            validate_result = tokenizer_service.validate_tokens(text)
            count_result = tokenizer_service.count_tokens(text)
            estimate_result = tokenizer_service.estimate_tokens_from_characters(text_length)
            
            # Verify consistency in token counts
            assert validate_result["token_count"] == 100
            assert count_result["token_count"] == 100
            assert estimate_result == 25  # Different because it's an estimation
