import pytest
from unittest.mock import patch, MagicMock, PropertyMock
import tiktoken

from app.ai.core.services.tokenizer_core_service import TokenizerService, TokenizerError


class TestTokenizerService:
    """Tests for the TokenizerService class"""

    def test_init(self, openai_settings):
        """Test initialization"""
        service = TokenizerService(openai_settings)
        assert service.settings == openai_settings

    def test_validate_tokens_success(self, openai_settings):
        """Test successful token validation"""
        # Mock the tiktoken encoding
        mock_encoding = MagicMock()
        mock_encoding.encode.return_value = [1, 2, 3, 4, 5]  # 5 tokens
        
        # Mock model_config property using patch with return_value
        mock_model_config = {
            "encoding": "cl100k_base",
            "model": "gpt-4-test",
            "model_family": "gpt",
            "max_tokens": 1000,
            "context_window": 8000,
            "capabilities": {
                "supports_functions": True,
                "supports_vision": False,
                "supports_embeddings": True
            }
        }
        
        with patch("app.ai.core.services.tokenizer_core_service.tiktoken.get_encoding", 
                  return_value=mock_encoding) as mock_get_encoding, \
             patch.object(openai_settings.__class__, "model_config", 
                   new_callable=PropertyMock, 
                   return_value=mock_model_config):
            
            # Create a service with mock settings
            service = TokenizerService(openai_settings)
            
            # Call the method
            result = service.validate_tokens("Test text")
            
            # Verify encoding was obtained
            mock_get_encoding.assert_called_once_with("cl100k_base")
            
            # Verify encoding was used to count tokens
            mock_encoding.encode.assert_called_once_with("Test text")
            
            # Verify result structure
            assert result["token_count"] == 5
            assert result["model_limit"] == 1000
            assert result["tokens_remaining"] == 995
            assert result["percentage_used"] == 0.5
            assert result["model"] == "gpt-4-test"
            assert result["model_family"] == "gpt"
            assert result["capabilities"] == {
                "supports_functions": True,
                "supports_vision": False,
                "supports_embeddings": True
            }
            assert result["encoding"] == "cl100k_base"

    def test_validate_tokens_with_fallback_encoding(self, openai_settings):
        """Test token validation with fallback encoding when not specified"""
        # Mock the tiktoken encoding
        mock_encoding = MagicMock()
        mock_encoding.encode.return_value = [1, 2, 3]  # 3 tokens
        
        # Mock model_config with missing encoding
        mock_model_config = {
            "model": "gpt-4-test",
            "model_family": "gpt",
            "max_tokens": 1000,
            "context_window": 8000,
            "capabilities": {}
        }
        
        with patch("app.ai.core.services.tokenizer_core_service.tiktoken.get_encoding", 
                  return_value=mock_encoding) as mock_get_encoding, \
             patch.object(openai_settings.__class__, "model_config", 
                   new_callable=PropertyMock, 
                   return_value=mock_model_config):
            
            # Create a service with mock settings
            service = TokenizerService(openai_settings)
            
            # Call the method
            result = service.validate_tokens("Test text")
            
            # Verify encoding was obtained with fallback
            mock_get_encoding.assert_called_once_with("cl100k_base")  # Default fallback
            
            # Verify encoding was used to count tokens
            mock_encoding.encode.assert_called_once_with("Test text")
            
            # Verify result structure with defaults
            assert result["token_count"] == 3
            assert result["model_limit"] == 1000
            assert result["encoding"] == "cl100k_base"

    def test_validate_tokens_error_handling(self, openai_settings):
        """Test error handling in token validation"""
        # Mock model_config with basic config
        mock_model_config = {
            "encoding": "cl100k_base"
        }
        
        with patch("app.ai.core.services.tokenizer_core_service.tiktoken.get_encoding", 
                  side_effect=Exception("Tiktoken error")) as mock_get_encoding, \
             patch.object(openai_settings.__class__, "model_config", 
                   new_callable=PropertyMock, 
                   return_value=mock_model_config):
            
            # Create a service with mock settings
            service = TokenizerService(openai_settings)
            
            # Call the method and check exception
            with pytest.raises(TokenizerError) as excinfo:
                service.validate_tokens("Test text")
            
            # Verify error message
            assert "Error validating tokens" in str(excinfo.value)
            assert "Tiktoken error" in str(excinfo.value)

    def test_count_tokens_success(self, openai_settings):
        """Test successful token counting"""
        # Mock the tiktoken encoding
        mock_encoding = MagicMock()
        mock_encoding.encode.return_value = [1, 2, 3, 4]  # 4 tokens
        
        # Mock model_config property
        mock_model_config = {
            "encoding": "cl100k_base",
            "model": "gpt-4-test",
            "model_family": "gpt",
            "context_window": 8000,
            "capabilities": {
                "supports_functions": True
            }
        }
        
        with patch("app.ai.core.services.tokenizer_core_service.tiktoken.get_encoding", 
                  return_value=mock_encoding) as mock_get_encoding, \
             patch.object(openai_settings.__class__, "model_config", 
                   new_callable=PropertyMock, 
                   return_value=mock_model_config):
            
            # Create a service with mock settings
            service = TokenizerService(openai_settings)
            
            # Call the method
            result = service.count_tokens("Test text")
            
            # Verify encoding was obtained
            mock_get_encoding.assert_called_once_with("cl100k_base")
            
            # Verify encoding was used to count tokens
            mock_encoding.encode.assert_called_once_with("Test text")
            
            # Verify result structure
            assert result["token_count"] == 4
            assert result["model"] == "gpt-4-test"
            assert result["model_family"] == "gpt"
            assert result["model_limit"] == 8000
            assert result["tokens_remaining"] == 7996
            assert result["is_near_limit"] is False  # 4/8000 is not near limit
            assert result["exceeds_limit"] is False

    def test_count_tokens_near_limit(self, openai_settings):
        """Test token counting near the limit"""
        # Mock the tiktoken encoding to return many tokens
        mock_encoding = MagicMock()
        mock_encoding.encode.return_value = [i for i in range(7600)]  # 7600 tokens (95% of 8000)
        
        # Mock model_config property
        mock_model_config = {
            "encoding": "cl100k_base",
            "model": "gpt-4-test",
            "model_family": "gpt",
            "context_window": 8000,
            "capabilities": {}
        }
        
        with patch("app.ai.core.services.tokenizer_core_service.tiktoken.get_encoding", 
                  return_value=mock_encoding), \
             patch.object(openai_settings.__class__, "model_config", 
                   new_callable=PropertyMock, 
                   return_value=mock_model_config):
            
            # Create a service with mock settings
            service = TokenizerService(openai_settings)
            
            # Call the method
            result = service.count_tokens("Test text")
            
            # Verify result flags
            assert result["token_count"] == 7600
            assert result["is_near_limit"] is True
            assert result["exceeds_limit"] is False
            assert result["tokens_remaining"] == 400

    def test_count_tokens_exceeds_limit(self, openai_settings):
        """Test token counting that exceeds the limit"""
        # Mock the tiktoken encoding to return too many tokens
        mock_encoding = MagicMock()
        mock_encoding.encode.return_value = [i for i in range(9000)]  # 9000 tokens (exceeds 8000)
        
        # Mock model_config property
        mock_model_config = {
            "encoding": "cl100k_base",
            "model": "gpt-4-test",
            "model_family": "gpt",
            "context_window": 8000,
            "capabilities": {}
        }
        
        with patch("app.ai.core.services.tokenizer_core_service.tiktoken.get_encoding", 
                  return_value=mock_encoding), \
             patch.object(openai_settings.__class__, "model_config", 
                   new_callable=PropertyMock, 
                   return_value=mock_model_config):
            
            # Create a service with mock settings
            service = TokenizerService(openai_settings)
            
            # Call the method
            result = service.count_tokens("Test text")
            
            # Verify result flags
            assert result["token_count"] == 9000
            assert result["is_near_limit"] is True
            assert result["exceeds_limit"] is True
            assert result["tokens_remaining"] == 0  # No tokens remaining when over limit

    def test_estimate_tokens_from_characters(self, openai_settings):
        """Test token estimation from character count"""
        service = TokenizerService(openai_settings)
        
        # Test various character counts
        assert service.estimate_tokens_from_characters(100) == 25  # 100/4 = 25
        assert service.estimate_tokens_from_characters(127) == 31  # 127/4 = 31.75, truncated to 31
        assert service.estimate_tokens_from_characters(4) == 1    # 4/4 = 1
        assert service.estimate_tokens_from_characters(3) == 0    # 3/4 = 0.75, truncated to 0
