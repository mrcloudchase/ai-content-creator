import tiktoken
from typing import Dict, Any, Optional, Tuple

class TokenServiceError(Exception):
    """Custom exception for token service errors"""
    pass

class TokenService:
    """Service for counting tokens for OpenAI models"""
    
    # Model context limits (approximate max tokens)
    MODEL_LIMITS = {
        "gpt-3.5-turbo": 4096,
        "gpt-3.5-turbo-16k": 16384,
        "gpt-4": 8192,
        "gpt-4-32k": 32768,
        "gpt-4-turbo": 128000,
    }
    
    # Default model to use
    DEFAULT_MODEL = "gpt-3.5-turbo"
    
    @staticmethod
    def count_tokens(text: str, model_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Count tokens in a text string for a specific model
        
        Args:
            text: The text to count tokens for
            model_name: Optional model name (defaults to gpt-3.5-turbo)
            
        Returns:
            Dictionary with token count and related information
            
        Raises:
            TokenServiceError: If there's an error counting tokens
        """
        # Input validation
        assert text is not None, "Text cannot be None"
        
        # Use default model if none specified
        model = model_name or TokenService.DEFAULT_MODEL
        
        try:
            # Get the encoding for the model
            encoding = TokenService._get_encoding(model)
            
            # Count the tokens
            token_count = len(encoding.encode(text))
            
            # Get the model's context limit
            context_limit = TokenService.MODEL_LIMITS.get(model, 4096)
            
            # Calculate percentage of context used
            context_percentage = (token_count / context_limit) * 100
            
            # Check if we're approaching or exceeding the limit
            is_near_limit = context_percentage > 75
            exceeds_limit = context_percentage > 100
            
            # Calculate tokens remaining
            tokens_remaining = context_limit - token_count if token_count < context_limit else 0
            
            # Return information about tokens
            result = {
                "token_count": token_count,
                "model": model,
                "model_limit": context_limit,
                "percentage_used": round(context_percentage, 2),
                "tokens_remaining": tokens_remaining,
                "is_near_limit": is_near_limit,
                "exceeds_limit": exceeds_limit
            }
            
            return result
        except Exception as e:
            raise TokenServiceError(f"Error counting tokens: {str(e)}")
    
    @staticmethod
    def _get_encoding(model: str):
        """
        Get the encoding for a specific model
        
        Args:
            model: The model name
            
        Returns:
            Encoding for the model
            
        Raises:
            TokenServiceError: If the encoding can't be determined
        """
        try:
            # For most current models
            if model in ["gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4", "gpt-4-32k", "gpt-4-turbo"]:
                return tiktoken.encoding_for_model(model)
            
            # Default to cl100k_base for newer models
            return tiktoken.get_encoding("cl100k_base")
        except Exception as e:
            raise TokenServiceError(f"Error getting encoding for model {model}: {str(e)}")
    
    @staticmethod
    def estimate_tokens_from_characters(text_length: int) -> int:
        """
        Rough estimate of tokens from character count
        (approximately 4 characters per token for English text)
        
        Args:
            text_length: The length of the text in characters
            
        Returns:
            Estimated token count
        """
        return text_length // 4 