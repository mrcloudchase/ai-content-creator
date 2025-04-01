import pytest
from unittest.mock import patch, MagicMock
import os
from pydantic import ValidationError

from app.config.settings import OpenAISettings


class TestOpenAISettings:
    """Tests for the OpenAISettings class"""
    
    def test_init_with_default_values(self):
        """Test initialization with default values"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key"}):
            settings = OpenAISettings()
            
            # Check default values
            assert settings.api_key == "test-api-key"
            assert settings.default_model == "gpt-4"  # Default from the class
            assert settings.temperature == 0.7
            assert settings.max_tokens == 150
            # Since the tests are using a fixture with 'test-org', we'll just check that organization is set
            assert settings.organization is not None
    
    def test_init_with_custom_values(self):
        """Test initialization with custom values"""
        settings = OpenAISettings(
            api_key="custom-api-key",
            organization="custom-org",
            default_model="gpt-3.5-turbo",
            temperature=0.5,
            max_tokens=200
        )
        
        # Check custom values
        assert settings.api_key == "custom-api-key"
        assert settings.organization == "custom-org"
        assert settings.default_model == "gpt-3.5-turbo"
        assert settings.temperature == 0.5
        assert settings.max_tokens == 200
    
    def test_init_without_api_key(self):
        """Test initialization without API key raises error"""
        # Remove API key from environment
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValidationError) as excinfo:
                OpenAISettings()
            
            # Check that the error is about the API key
            assert "api_key" in str(excinfo.value)
            assert "field required" in str(excinfo.value).lower()
    
    def test_model_family_property(self):
        """Test the model_family property"""
        # Test with different model names
        settings = OpenAISettings(api_key="test", default_model="gpt-4")
        assert settings.model_family == "gpt"
        
        settings = OpenAISettings(api_key="test", default_model="gpt-3.5-turbo")
        assert settings.model_family == "gpt"
        
        settings = OpenAISettings(api_key="test", default_model="o1-preview")
        assert settings.model_family == "o1"
    
    def test_encoding_property(self):
        """Test the encoding property"""
        # Test with direct access
        settings = OpenAISettings(api_key="test", default_model="gpt-4", encoding="cl100k_base")
        
        # Check encoding
        assert settings.encoding == "cl100k_base"
    
    def test_model_settings_property(self):
        """Test the model_settings property"""
        with patch("app.config.settings.tiktoken.get_encoding") as mock_get_encoding:
            # Set up the mock
            mock_encoding = MagicMock()
            mock_encoding.name = "cl100k_base"
            mock_encoding.max_tokens = 8192
            mock_get_encoding.return_value = mock_encoding
            
            # Create settings
            settings = OpenAISettings(api_key="test", default_model="gpt-4", encoding="cl100k_base")
            
            # Get model settings
            model_settings = settings.model_settings
            
            # Check the structure
            assert model_settings["encoding"] == "cl100k_base"
            assert model_settings["model"] == "gpt-4"
            assert model_settings["model_family"] == "gpt"
            assert model_settings["context_window"] == 8192
            assert "capabilities" in model_settings
    
    def test_model_settings_property_exception_handling(self):
        """Test model_settings property exception handling"""
        with patch("app.config.settings.tiktoken.get_encoding", side_effect=Exception("Error")):
            # Create settings
            settings = OpenAISettings(api_key="test", default_model="gpt-4")
            
            # Get model settings (should not raise exception)
            model_settings = settings.model_settings
            
            # Check that we got fallback values
            assert model_settings["encoding"] == "cl100k_base"
            assert model_settings["max_tokens"] == 4096
            assert model_settings["context_window"] == 4096
            assert model_settings["model"] == "gpt-4"
            assert model_settings["model_family"] == "unknown"
            assert "capabilities" in model_settings
    
    def test_get_model_capabilities(self):
        """Test the _get_model_capabilities method"""
        settings = OpenAISettings(api_key="test")
        
        # Test with different model families
        gpt_capabilities = settings._get_model_capabilities("gpt")
        assert gpt_capabilities["supports_functions"] is True
        
        o1_capabilities = settings._get_model_capabilities("o1")
        assert o1_capabilities["supports_vision"] is True
        
        unknown_capabilities = settings._get_model_capabilities("unknown")
        assert unknown_capabilities["supports_functions"] is False
        assert unknown_capabilities["supports_vision"] is False
        
        # Test with non-existent model family (should return unknown capabilities)
        nonexistent_capabilities = settings._get_model_capabilities("nonexistent")
        assert nonexistent_capabilities == unknown_capabilities
