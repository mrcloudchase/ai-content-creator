import pytest
from app.services.token_service import TokenService, TokenServiceError

def test_count_tokens_simple_text():
    """Test counting tokens for simple text"""
    # Arrange
    text = "Hello, world!"
    
    # Act
    result = TokenService.count_tokens(text)
    
    # Assert
    assert result["token_count"] > 0
    assert result["model"] == "gpt-3.5-turbo"
    assert result["model_limit"] == 4096
    assert result["percentage_used"] < 1  # Should be a very small percentage
    assert not result["is_near_limit"]
    assert not result["exceeds_limit"]
    assert result["tokens_remaining"] > 0

def test_count_tokens_different_model():
    """Test counting tokens with a different model"""
    # Arrange
    text = "Hello, world!"
    model = "gpt-4"
    
    # Act
    result = TokenService.count_tokens(text, model)
    
    # Assert
    assert result["token_count"] > 0
    assert result["model"] == "gpt-4"
    assert result["model_limit"] == 8192
    assert result["percentage_used"] < 1  # Should be a very small percentage

def test_count_tokens_longer_text():
    """Test counting tokens for longer text"""
    # Arrange
    # Generate a text that's definitely more than a few tokens
    text = "This is a longer text. " * 100
    
    # Act
    result = TokenService.count_tokens(text)
    
    # Assert
    assert result["token_count"] > 100  # Should have more than 100 tokens
    assert result["percentage_used"] > 1  # Should be a higher percentage than the simple test

def test_count_tokens_with_special_characters():
    """Test counting tokens with special characters"""
    # Arrange
    text = "Special characters like: é, ñ, ü, and emoji like: 😀 🚀 🌟"
    
    # Act
    result = TokenService.count_tokens(text)
    
    # Assert
    assert result["token_count"] > 0
    # Emojis and special characters often take more tokens
    assert result["token_count"] > len(text) / 10

def test_count_tokens_empty_string():
    """Test counting tokens for an empty string"""
    # Arrange
    text = ""
    
    # Act
    result = TokenService.count_tokens(text)
    
    # Assert
    assert result["token_count"] == 0
    assert result["percentage_used"] == 0
    assert result["tokens_remaining"] == result["model_limit"]

def test_estimate_tokens_from_characters():
    """Test estimating tokens from character count"""
    # Arrange
    char_count = 100
    
    # Act
    result = TokenService.estimate_tokens_from_characters(char_count)
    
    # Assert
    assert result == 25  # Should be 100 / 4 = 25 