import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import HTTPException
from app.ai.content_generate.routers.content_generate_router import (
    validate_token_count,
    generate_content_for_type,
    generate_all_content,
    format_response,
    ContentGenerateRouterError
)
from app.ai.content_generate.models.content_generate_model import (
    ContentTypeRequest,
    ContentGenerateRequest,
    GeneratedContent,
    ContentGenerateResponse
)
from app.ai.core.services.tokenizer_core_service import TokenizerError

class TestContentGenerateRouter:
    """Unit tests for the content generate router functions"""
    
    @patch("app.ai.content_generate.routers.content_generate_router.tokenizer_service")
    def test_validate_token_count_success(self, mock_tokenizer_service):
        """Test token count validation success"""
        # Setup mock
        mock_token_info = {
            "token_count": 1000,
            "model_limit": 4000,
            "percentage_used": 25,
            "tokens_remaining": 3000
        }
        mock_tokenizer_service.validate_tokens.return_value = mock_token_info
        
        # Call function
        result = validate_token_count("Sample text")
        
        # Verify result
        assert result == mock_token_info
        mock_tokenizer_service.validate_tokens.assert_called_once_with("Sample text")
    
    @patch("app.ai.content_generate.routers.content_generate_router.tokenizer_service")
    def test_validate_token_count_tokenizer_error(self, mock_tokenizer_service):
        """Test token count validation with TokenizerError"""
        # Setup mock to raise error
        mock_tokenizer_service.validate_tokens.side_effect = TokenizerError("Token limit exceeded")
        
        # Call function and expect error
        with pytest.raises(ContentGenerateRouterError) as excinfo:
            validate_token_count("Sample text")
            
        # Verify error message
        assert "Tokenizer error: Token limit exceeded" in str(excinfo.value)
    
    @patch("app.ai.content_generate.routers.content_generate_router.content_generate_service")
    @patch("app.ai.content_generate.routers.content_generate_router.ai_service")
    @pytest.mark.asyncio
    async def test_generate_content_for_type_success(self, mock_ai_service, mock_content_generate_service):
        """Test generating content for a specific type"""
        # Setup mocks
        mock_prompt = {"messages": [{"role": "system", "content": "test"}, {"role": "user", "content": "test"}]}
        mock_content_generate_service.format_content_generate_prompt.return_value = mock_prompt
        
        mock_completion = {"text": "# Generated Content\n\nThis is a test content."}
        mock_ai_service.generate_completion = AsyncMock(return_value=mock_completion)
        
        # Call function
        result = await generate_content_for_type(
            content_type="tutorial",
            title="Test Title",
            intent="Test intent",
            text="Test text"
        )
        
        # Verify result
        assert result == mock_completion["text"]
        mock_content_generate_service.format_content_generate_prompt.assert_called_once_with(
            content_type="tutorial",
            intent="Test intent",
            text="Test text",
            title="Test Title"
        )
        mock_ai_service.generate_completion.assert_called_once()
    
    @patch("app.ai.content_generate.routers.content_generate_router.content_generate_service")
    @patch("app.ai.content_generate.routers.content_generate_router.ai_service")
    @pytest.mark.asyncio
    async def test_generate_content_for_type_empty_response(self, mock_ai_service, mock_content_generate_service):
        """Test error handling when AI returns empty response"""
        # Setup mocks
        mock_prompt = {"messages": [{"role": "system", "content": "test"}, {"role": "user", "content": "test"}]}
        mock_content_generate_service.format_content_generate_prompt.return_value = mock_prompt
        
        # Empty response
        mock_completion = {"text": ""}
        mock_ai_service.generate_completion = AsyncMock(return_value=mock_completion)
        
        # Call function and expect error
        with pytest.raises(ContentGenerateRouterError) as excinfo:
            await generate_content_for_type(
                content_type="tutorial",
                title="Test Title",
                intent="Test intent",
                text="Test text"
            )
            
        # Verify error message
        assert "Empty response from LLM" in str(excinfo.value)
    
    @patch("app.ai.content_generate.routers.content_generate_router.generate_content_for_type")
    @pytest.mark.asyncio
    async def test_generate_all_content_success(self, mock_generate_content_for_type):
        """Test generating content for multiple types"""
        # Setup mock
        mock_generate_content_for_type.side_effect = [
            "# Tutorial Content\n\nThis is tutorial content.",
            "# How-To Guide\n\nThis is how-to content."
        ]
        
        # Test request data
        request = ContentGenerateRequest(
            intent="Test intent",
            text_used="Test text",
            content_types=[
                ContentTypeRequest(type="tutorial", title="Test Tutorial"),
                ContentTypeRequest(type="how-to", title=None)
            ]
        )
        
        token_info = {"model": "gpt-4"}
        
        # Call function
        result = await generate_all_content(request, token_info)
        
        # Verify result
        assert len(result) == 2
        assert result[0].type == "tutorial"
        assert result[0].title == "Test Tutorial"
        assert result[0].content == "# Tutorial Content\n\nThis is tutorial content."
        assert result[1].type == "how-to"
        assert result[1].title == "How-To Guide"  # Extracted from content
        assert result[1].content == "# How-To Guide\n\nThis is how-to content."
    
    @patch("app.ai.content_generate.routers.content_generate_router.generate_content_for_type")
    @pytest.mark.asyncio
    async def test_generate_all_content_partial_failure(self, mock_generate_content_for_type):
        """Test handling when one content type generation fails but others succeed"""
        # Setup mock - first call succeeds, second call fails
        mock_generate_content_for_type.side_effect = [
            "# Tutorial Content\n\nThis is tutorial content.",
            ContentGenerateRouterError("Failed to generate how-to content")
        ]
        
        # Test request data
        request = ContentGenerateRequest(
            intent="Test intent",
            text_used="Test text",
            content_types=[
                ContentTypeRequest(type="tutorial", title="Test Tutorial"),
                ContentTypeRequest(type="how-to", title="Test How-To")
            ]
        )
        
        token_info = {"model": "gpt-4"}
        
        # Call function
        result = await generate_all_content(request, token_info)
        
        # Verify result - should still have the successful content
        assert len(result) == 1
        assert result[0].type == "tutorial"
        assert result[0].title == "Test Tutorial"
        assert result[0].content == "# Tutorial Content\n\nThis is tutorial content."
    
    @patch("app.ai.content_generate.routers.content_generate_router.generate_content_for_type")
    @pytest.mark.asyncio
    async def test_generate_all_content_all_fail(self, mock_generate_content_for_type):
        """Test handling when all content type generations fail"""
        # Setup mock - all calls fail
        mock_generate_content_for_type.side_effect = ContentGenerateRouterError("Failed to generate content")
        
        # Test request data
        request = ContentGenerateRequest(
            intent="Test intent",
            text_used="Test text",
            content_types=[
                ContentTypeRequest(type="tutorial", title="Test Tutorial"),
                ContentTypeRequest(type="how-to", title="Test How-To")
            ]
        )
        
        token_info = {"model": "gpt-4"}
        
        # Call function and expect error
        with pytest.raises(ContentGenerateRouterError) as excinfo:
            await generate_all_content(request, token_info)
            
        # Verify error message
        assert "Failed to generate content for all requested types" in str(excinfo.value)
    
    def test_format_response_valid_data(self):
        """Test format_response with valid data"""
        # Test data
        generated_content = [
            GeneratedContent(
                type="tutorial",
                title="Test Tutorial",
                content="# Test Tutorial\n\nContent here."
            ),
            GeneratedContent(
                type="how-to",
                title="Test How-To",
                content="# Test How-To\n\nSteps here."
            )
        ]
        
        token_info = {
            "model": "gpt-4",
            "model_family": "gpt",
            "capabilities": {"supports_functions": True},
            "usage": {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150},
            "model_limit": 4000,
            "token_count": 1000,
            "tokens_remaining": 3000
        }
        
        text_used = "Sample text"
        
        # Call function
        result = format_response(generated_content, token_info, text_used)
        
        # Verify result
        assert isinstance(result, ContentGenerateResponse)
        assert len(result.generated_content) == 2
        assert result.model == "gpt-4"
        assert result.model_family == "gpt"
        assert result.capabilities == {"supports_functions": True}
        assert result.usage == {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150}
        assert result.token_limit == 4000
        assert result.token_count == 1000
        assert result.remaining_tokens == 3000
        assert result.text_used == "Sample text"
        
    def test_format_response_missing_data(self):
        """Test format_response with missing data in token_info"""
        # Test data with missing fields
        generated_content = [
            GeneratedContent(
                type="tutorial",
                title="Test Tutorial",
                content="# Test Tutorial\n\nContent here."
            )
        ]
        
        # Minimal token info
        token_info = {
            "model": "gpt-4"
        }
        
        text_used = "Sample text"
        
        # Call function
        result = format_response(generated_content, token_info, text_used)
        
        # Verify result - should use defaults for missing values
        assert isinstance(result, ContentGenerateResponse)
        assert result.model == "gpt-4"
        assert result.model_family == "unknown"
        assert result.capabilities == {}
        assert result.usage == {}
        assert result.token_limit == 0
        assert result.token_count == 0
        assert result.remaining_tokens == 0 