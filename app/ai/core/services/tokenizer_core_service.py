import tiktoken
from typing import Dict, Any, Optional
from app.config.settings import OpenAISettings
import logging
import traceback

logger = logging.getLogger(__name__)

class TokenizerError(Exception):
    """Custom exception for tokenizer service errors"""
    pass

class TokenizerService:
    """Service for counting and validating tokens for OpenAI models"""
    
    def __init__(self, settings: OpenAISettings):
        self.settings = settings
    
    def validate_tokens(self, text: str) -> Dict[str, Any]:
        """
        Validate text against token limits
        
        Args:
            text: Text to validate
            
        Returns:
            Dictionary with token information
            
        Raises:
            TokenizerError: If token validation fails
        """
        try:
            # Get model configuration
            model_config = self.settings.model_config
            
            # Log configuration for debugging
            logger.debug(f"Model config received: {model_config}")
            
            # Get encoding with fallback
            encoding_name = model_config.get("encoding")
            if not encoding_name:
                logger.warning("No encoding found in model config, using fallback")
                encoding_name = "cl100k_base"  # Common fallback encoding
            
            # Get encoding
            encoding = tiktoken.get_encoding(encoding_name)
            
            # Count tokens
            token_count = len(encoding.encode(text))
            
            # Get model limits
            model_limit = model_config.get("max_tokens", 4096)  # Default fallback
            context_window = model_config.get("context_window", 8192)  # Default fallback
            
            # Calculate remaining tokens
            tokens_remaining = model_limit - token_count
            percentage_used = (token_count / model_limit) * 100
            
            # Build response
            token_info = {
                "token_count": token_count,
                "model_limit": model_limit,
                "tokens_remaining": tokens_remaining,
                "percentage_used": percentage_used,
                "model": model_config.get("model", "unknown"),
                "model_family": model_config.get("model_family", "unknown"),
                "capabilities": model_config.get("capabilities", {}),
                "encoding": encoding_name
            }
            
            logger.debug(f"Token validation complete: {token_info}")
            return token_info
            
        except Exception as e:
            logger.error(f"Error validating tokens: {str(e)}")
            logger.error(f"Error type: {type(e)}")
            logger.error(f"Error traceback: {traceback.format_exc()}")
            raise TokenizerError(f"Error validating tokens: {str(e)}")
    
    def count_tokens(self, text: str, model_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Count tokens in a text string for a specific model
        
        Args:
            text: The text to count tokens for
            model_name: Optional model name (defaults to configured model)
            
        Returns:
            Dictionary with token count and related information
            
        Raises:
            TokenizerError: If there's an error counting tokens
        """
        # Input validation
        assert text is not None, "Text cannot be None"
        assert text.strip(), "Text cannot be empty"
        
        try:
            # Get model configuration
            model_config = self.settings.model_config
            
            # Get the encoding
            encoding = tiktoken.get_encoding(model_config["encoding"])
            
            # Count the tokens
            token_count = len(encoding.encode(text))
            
            # Get the model's context window
            context_window = model_config["context_window"]
            
            # Calculate percentage of context used
            context_percentage = (token_count / context_window) * 100
            
            # Check if we're approaching or exceeding the limit
            is_near_limit = context_percentage > 75
            exceeds_limit = context_percentage > 100
            
            # Calculate tokens remaining
            tokens_remaining = context_window - token_count if token_count < context_window else 0
            
            # Return information about tokens
            return {
                "token_count": token_count,
                "model": model_config["model"],
                "model_family": model_config["model_family"],
                "model_limit": context_window,
                "percentage_used": round(context_percentage, 2),
                "tokens_remaining": tokens_remaining,
                "is_near_limit": is_near_limit,
                "exceeds_limit": exceeds_limit,
                "capabilities": model_config["capabilities"]
            }
        except AssertionError as e:
            raise TokenizerError(str(e))
        except Exception as e:
            raise TokenizerError(f"Error counting tokens: {str(e)}")
    
    def estimate_tokens_from_characters(self, text_length: int) -> int:
        """
        Rough estimate of tokens from character count
        (approximately 4 characters per token for English text)
        
        Args:
            text_length: The length of the text in characters
            
        Returns:
            Estimated token count
        """
        return text_length // 4 