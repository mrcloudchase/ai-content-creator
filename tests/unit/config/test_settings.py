import pytest
import os
from app.config.settings import OpenAISettings

def test_openai_settings_defaults():
    """Test default values for OpenAI settings."""
    # Use the environment variable, but with a temporary override
    original_api_key = os.environ.get('OPENAI_API_KEY')
    try:
        os.environ['OPENAI_API_KEY'] = 'test-api-key'
        settings = OpenAISettings()
        
        # Check default values
        assert settings.api_key == 'test-api-key'
        assert settings.default_model == 'gpt-3.5-turbo'
        assert settings.max_tokens == 1000
        assert settings.temperature == 0.7
        assert settings.organization is None
    finally:
        # Restore the original environment variable
        if original_api_key:
            os.environ['OPENAI_API_KEY'] = original_api_key
        elif 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']

def test_openai_settings_custom_values():
    """Test custom values for OpenAI settings."""
    # Set environment variables with custom values
    original_values = {}
    custom_values = {
        'OPENAI_API_KEY': 'custom-api-key',
        'OPENAI_DEFAULT_MODEL': 'gpt-4',
        'OPENAI_MAX_TOKENS': '2048',
        'OPENAI_TEMPERATURE': '0.5',
        'OPENAI_ORGANIZATION': 'test-org'
    }
    
    try:
        # Save original values and set custom values
        for key, value in custom_values.items():
            original_values[key] = os.environ.get(key)
            os.environ[key] = value
        
        # Create settings with the custom environment values
        settings = OpenAISettings()
        
        # Verify custom values were applied
        assert settings.api_key == 'custom-api-key'
        assert settings.default_model == 'gpt-4'
        assert settings.max_tokens == 2048
        assert settings.temperature == 0.5
        assert settings.organization == 'test-org'
    finally:
        # Restore original environment variables
        for key, value in original_values.items():
            if value is not None:
                os.environ[key] = value
            elif key in os.environ:
                del os.environ[key]

def test_openai_settings_validation():
    """Test validation in OpenAI settings."""
    # Test that validation fails when API key is empty
    original_api_key = os.environ.get('OPENAI_API_KEY')
    try:
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        
        with pytest.raises(Exception):
            OpenAISettings()
    finally:
        if original_api_key:
            os.environ['OPENAI_API_KEY'] = original_api_key 