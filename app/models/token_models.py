from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class TokenCountRequest(BaseModel):
    """Request model for token counting"""
    text: str = Field(..., description="The text to count tokens for")
    model: Optional[str] = Field(None, description="The model to use for token counting (defaults to gpt-3.5-turbo)")

class TokenCountResponse(BaseModel):
    """Response model for token counting"""
    token_count: int = Field(..., description="Number of tokens in the text")
    model: str = Field(..., description="Model used for token counting")
    model_limit: int = Field(..., description="Token limit for the model")
    percentage_used: float = Field(..., description="Percentage of model context used")
    tokens_remaining: int = Field(..., description="Number of tokens remaining in model context")
    is_near_limit: bool = Field(..., description="Whether the token count is approaching the limit (>75%)")
    exceeds_limit: bool = Field(..., description="Whether the token count exceeds the model limit") 