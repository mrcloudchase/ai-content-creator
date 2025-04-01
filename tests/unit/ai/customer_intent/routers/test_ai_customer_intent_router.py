import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import io

from app.ai.customer_intent.routers.ai_customer_intent_router import (
    extract_file_content,
    process_text,
    validate_token_count,
    generate_intent,
    format_response,
    CustomerIntentRouterError
)
from app.input_processing.core.services.file_handler_routing_logic_core_services import FileHandlerRoutingError
from app.input_processing.core.services.input_processing_core_service import InputProcessingError
from app.ai.core.services.tokenizer_core_service import TokenizerError
from app.ai.core.services.ai_core_service import OpenAIServiceError


class TestCustomerIntentRouter:
    """Unit tests for customer intent router helper functions"""
    
    @pytest.mark.asyncio
    async def test_extract_file_content_markdown(self, mock_markdown_upload):
        """Test extracting content from markdown file"""
        # Mock file handler and markdown service
        with patch("app.ai.customer_intent.routers.ai_customer_intent_router.file_handler_routing_service.validate_file_type", 
                  return_value="markdown"), \
             patch("app.ai.customer_intent.routers.ai_customer_intent_router.markdown_service.extract_text", 
                  return_value="Extracted markdown text"):
            
            # Call function
            result = await extract_file_content(mock_markdown_upload)
            
            # Verify result
            assert result == "Extracted markdown text"
    
    @pytest.mark.asyncio
    async def test_extract_file_content_docx(self, mock_docx_upload):
        """Test extracting content from docx file"""
        # Mock file handler and docx service
        with patch("app.ai.customer_intent.routers.ai_customer_intent_router.file_handler_routing_service.validate_file_type", 
                  return_value="docx"), \
             patch("app.ai.customer_intent.routers.ai_customer_intent_router.docx_service.extract_text", 
                  return_value="Extracted docx text"):
            
            # Call function
            result = await extract_file_content(mock_docx_upload)
            
            # Verify result
            assert result == "Extracted docx text"
    
    @pytest.mark.asyncio
    async def test_extract_file_content_unsupported_type(self, mock_markdown_upload):
        """Test extracting content with unsupported file type"""
        # Mock file handler to return unsupported type
        with patch("app.ai.customer_intent.routers.ai_customer_intent_router.file_handler_routing_service.validate_file_type", 
                  return_value="pdf"):  # Unsupported type
            
            # Call function and expect error
            with pytest.raises(CustomerIntentRouterError) as excinfo:
                await extract_file_content(mock_markdown_upload)
            
            # Verify error message
            assert "Unsupported file type: pdf" in str(excinfo.value)
    
    @pytest.mark.asyncio
    async def test_extract_file_content_file_handler_error(self, mock_markdown_upload):
        """Test extracting content with file handler error"""
        # Mock file handler to raise error
        with patch("app.ai.customer_intent.routers.ai_customer_intent_router.file_handler_routing_service.validate_file_type", 
                  side_effect=FileHandlerRoutingError("Invalid file extension")):
            
            # Call function and expect error
            with pytest.raises(CustomerIntentRouterError) as excinfo:
                await extract_file_content(mock_markdown_upload)
            
            # Verify error message
            assert "Invalid file type:" in str(excinfo.value)
            assert "Invalid file extension" in str(excinfo.value)
    
    def test_process_text_success(self):
        """Test successful text processing"""
        # Mock InputProcessingService
        with patch("app.ai.customer_intent.routers.ai_customer_intent_router.InputProcessingService.process_text", 
                  return_value="Processed text"):
            
            # Call function
            result = process_text("Raw text")
            
            # Verify result
            assert result == "Processed text"
    
    def test_process_text_empty_input(self):
        """Test process_text with empty input"""
        # Mock InputProcessingService to raise error
        with patch("app.ai.customer_intent.routers.ai_customer_intent_router.InputProcessingService.process_text",
                  side_effect=InputProcessingError("Empty text cannot be processed")):
            
            # Call function and expect error
            with pytest.raises(CustomerIntentRouterError) as excinfo:
                process_text("")
            
            # Verify error message - updated to match the actual implementation
            assert "Document text cannot be empty" in str(excinfo.value)
    
    def test_validate_token_count_success(self):
        """Test successful token validation"""
        # Expected result
        expected_result = {
            "token_count": 100,
            "model_limit": 4096,
            "tokens_remaining": 3996,
            "percentage_used": 2.44,
            "model": "gpt-4",
            "model_family": "gpt",
            "capabilities": {"supports_functions": True},
            "encoding": "cl100k_base"
        }
        
        # Mock tokenizer service
        with patch("app.ai.customer_intent.routers.ai_customer_intent_router.tokenizer_service.validate_tokens", 
                  return_value=expected_result):
            
            # Call function
            result = validate_token_count("Test text")
            
            # Verify result
            assert result == expected_result
    
    def test_validate_token_count_tokenizer_error(self):
        """Test validate_token_count with tokenizer error"""
        # Mock tokenizer service to raise error
        with patch("app.ai.customer_intent.routers.ai_customer_intent_router.tokenizer_service.validate_tokens", 
                  side_effect=TokenizerError("Token limit exceeded")):
            
            # Call function and expect error
            with pytest.raises(CustomerIntentRouterError) as excinfo:
                validate_token_count("Test text")
            
            # Verify error message
            assert "Tokenizer error:" in str(excinfo.value)
            assert "Token limit exceeded" in str(excinfo.value)
    
    @pytest.mark.asyncio
    async def test_generate_intent_success(self):
        """Test successful intent generation"""
        # Mock prompt and AI result
        prompt_result = {
            "messages": [
                {"role": "system", "content": "You are an expert..."},
                {"role": "user", "content": "Please analyze..."}
            ]
        }
        
        ai_result = {
            "text": "As a content creator, I want to streamline my workflow because it saves time.",
            "model": "gpt-4",
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150
            }
        }
        
        # Mock services
        with patch("app.ai.customer_intent.routers.ai_customer_intent_router.customer_intent_service.format_customer_intent_prompt", 
                  return_value=prompt_result), \
             patch("app.ai.customer_intent.routers.ai_customer_intent_router.ai_service.generate_completion", 
                  new_callable=AsyncMock, return_value=ai_result):
            
            # Call function
            result = await generate_intent("Processed text")
            
            # Verify result
            assert result["intent"] == "As a content creator, I want to streamline my workflow because it saves time."
            assert result["model"] == "gpt-4"
            assert result["usage"] == ai_result["usage"]
    
    @pytest.mark.asyncio
    async def test_generate_intent_empty_text(self):
        """Test generate_intent with empty text"""
        # Call function with empty text and expect error
        with pytest.raises(CustomerIntentRouterError) as excinfo:
            await generate_intent("")
        
        # Verify error message
        assert "Text cannot be empty for intent generation" in str(excinfo.value)
    
    @pytest.mark.asyncio
    async def test_generate_intent_openai_error(self):
        """Test generate_intent with OpenAI error"""
        # Mock prompt
        prompt_result = {
            "messages": [
                {"role": "system", "content": "You are an expert..."},
                {"role": "user", "content": "Please analyze..."}
            ]
        }
        
        # Mock services with error
        with patch("app.ai.customer_intent.routers.ai_customer_intent_router.customer_intent_service.format_customer_intent_prompt", 
                  return_value=prompt_result), \
             patch("app.ai.customer_intent.routers.ai_customer_intent_router.ai_service.generate_completion", 
                  new_callable=AsyncMock, side_effect=OpenAIServiceError("API rate limit exceeded")):
            
            # Call function and expect error
            with pytest.raises(CustomerIntentRouterError) as excinfo:
                await generate_intent("Processed text")
            
            # Verify error message
            assert "AI service error:" in str(excinfo.value)
            assert "API rate limit exceeded" in str(excinfo.value)
    
    def test_format_response_success(self):
        """Test successful response formatting"""
        # Create test data
        intent_result = {
            "intent": "As a content creator, I want to streamline my workflow because it saves time.",
            "model": "gpt-4",
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150
            }
        }
        
        token_info = {
            "token_count": 100,
            "model_limit": 4096,
            "tokens_remaining": 3996,
            "percentage_used": 2.44,
            "model": "gpt-4",
            "model_family": "gpt",
            "capabilities": {"supports_functions": True},
            "encoding": "cl100k_base"
        }
        
        processed_text = "Processed text for testing"
        
        # Call function
        result = format_response(intent_result, token_info, processed_text)
        
        # Verify result structure
        assert result.intent == intent_result["intent"]
        assert result.model == intent_result["model"]
        assert result.model_family == token_info["model_family"]
        assert result.capabilities == token_info["capabilities"]
        assert result.usage == intent_result["usage"]
        assert result.token_limit == token_info["model_limit"]
        assert result.token_count == token_info["token_count"]
        assert result.remaining_tokens == token_info["tokens_remaining"]
        assert result.text_used == processed_text
    
    def test_format_response_missing_data(self):
        """Test format_response with missing data"""
        # Create incomplete data
        intent_result = {
            "model": "gpt-4",
            "usage": {"total_tokens": 150}
            # Missing intent
        }
        
        token_info = {
            "token_count": 100,
            "model_family": "gpt",
            # Missing model_limit
        }
        
        processed_text = "Processed text"
        
        # Call function and expect error
        with pytest.raises(CustomerIntentRouterError) as excinfo:
            format_response(intent_result, token_info, processed_text)
        
        # Verify error message
        assert "Error formatting response:" in str(excinfo.value)
