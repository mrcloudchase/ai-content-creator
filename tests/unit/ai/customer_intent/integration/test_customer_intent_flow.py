import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from app.ai.customer_intent.services.ai_customer_intent_service import CustomerIntentService
from app.ai.core.services.ai_core_service import AIService
from app.ai.core.services.tokenizer_core_service import TokenizerService
from app.config.settings import OpenAISettings


class TestCustomerIntentFlow:
    """Integration tests for customer intent flow"""
    
    @pytest.mark.asyncio
    async def test_customer_intent_service_with_ai_service(self, openai_settings, mock_openai_response):
        """Test integration between CustomerIntentService and AIService"""
        # Create services
        customer_intent_service = CustomerIntentService()
        ai_service = AIService(openai_settings)
        
        # Mock AI service to return a completion
        ai_result = {
            "text": "As a content creator, I want to streamline my workflow because it saves time and increases productivity.",
            "model": "gpt-4",
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150
            }
        }
        
        with patch.object(ai_service, 'generate_completion', new_callable=AsyncMock, return_value=ai_result):
            # Test document
            document_text = """# Content Creator Workflow
            
As a content creator, I need a better way to manage my workflow. The current process is time-consuming and inefficient.
I spend too much time switching between applications, formatting content, and scheduling posts.
A streamlined workflow would help me be more productive and focus on creating quality content."""
            
            # Step 1: Format the prompt using CustomerIntentService
            prompt_result = customer_intent_service.format_customer_intent_prompt(document_text)
            
            # Verify prompt structure
            assert "messages" in prompt_result
            assert len(prompt_result["messages"]) == 2
            assert prompt_result["messages"][0]["role"] == "system"
            assert "As a [user type], I want to [action] because [reason]" in prompt_result["messages"][0]["content"]
            assert prompt_result["messages"][1]["role"] == "user"
            assert document_text in prompt_result["messages"][1]["content"]
            
            # Step 2: Use the formatted prompt to generate a completion
            completion = await ai_service.generate_completion(messages=prompt_result["messages"])
            
            # Verify completion
            assert completion["text"] == "As a content creator, I want to streamline my workflow because it saves time and increases productivity."
            assert completion["model"] == "gpt-4"
            assert completion["usage"]["prompt_tokens"] == 100
            assert completion["usage"]["completion_tokens"] == 50
            assert completion["usage"]["total_tokens"] == 150
    
    @pytest.mark.asyncio
    async def test_customer_intent_with_specific_user_type(self, openai_settings, mock_openai_response):
        """Test customer intent flow with a specific user type"""
        # Create services
        customer_intent_service = CustomerIntentService()
        ai_service = AIService(openai_settings)
        
        # Mock AI service to return a completion
        ai_result = {
            "text": "As a product manager, I want to track feature usage because it helps prioritize development efforts.",
            "model": "gpt-4",
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150
            }
        }
        
        with patch.object(ai_service, 'generate_completion', new_callable=AsyncMock, return_value=ai_result):
            # Test document
            document_text = """# Feature Tracking Requirements
            
We need to improve our feature tracking system. Currently, we lack data on which features are most used by our customers.
This information would be valuable for prioritizing future development efforts.
The product team needs a way to collect, analyze, and report on feature usage."""
            
            # Step 1: Format the prompt with specific user type
            user_type = "product manager"
            prompt_result = customer_intent_service.format_customer_intent_prompt(document_text, user_type)
            
            # Verify prompt contains user type
            assert "messages" in prompt_result
            assert len(prompt_result["messages"]) == 2
            assert prompt_result["messages"][1]["role"] == "user"
            assert f"for a {user_type}" in prompt_result["messages"][1]["content"]
            
            # Step 2: Use the formatted prompt to generate a completion
            completion = await ai_service.generate_completion(messages=prompt_result["messages"])
            
            # Verify completion
            assert completion["text"] == "As a product manager, I want to track feature usage because it helps prioritize development efforts."
            assert completion["model"] == "gpt-4"
    
    def test_customer_intent_integration_with_token_validation(self, openai_settings):
        """Test customer intent flow with token validation"""
        # Create services
        customer_intent_service = CustomerIntentService()
        tokenizer_service = TokenizerService(openai_settings)
        
        # Mock token validation
        token_result = {
            "token_count": 120,
            "model_limit": 4096,
            "tokens_remaining": 3976,
            "percentage_used": 2.93,
            "model": "gpt-4",
            "model_family": "gpt",
            "capabilities": {"supports_functions": True},
            "encoding": "cl100k_base"
        }
        
        with patch.object(tokenizer_service, 'validate_tokens', return_value=token_result):
            # Test document
            document_text = """# Customer Survey Results
            
Our recent customer survey indicates that users want a simpler onboarding process.
Many respondents mentioned confusion during the initial setup, with most dropping off before completion.
We should focus on streamlining the onboarding flow to improve conversion rates."""
            
            # Step 1: Format the prompt
            prompt_result = customer_intent_service.format_customer_intent_prompt(document_text)
            
            # Verify prompt structure
            assert "messages" in prompt_result
            assert len(prompt_result["messages"]) == 2
            
            # Step 2: Get combined messages text for token validation
            combined_text = prompt_result["messages"][0]["content"] + prompt_result["messages"][1]["content"]
            
            # Step 3: Validate tokens
            token_info = tokenizer_service.validate_tokens(combined_text)
            
            # Verify token validation
            assert token_info["token_count"] == 120
            assert token_info["model_limit"] == 4096
            assert token_info["tokens_remaining"] == 3976
            
            # Step 4: Check if we should proceed based on token count
            should_proceed = token_info["token_count"] <= token_info["model_limit"]
            assert should_proceed
