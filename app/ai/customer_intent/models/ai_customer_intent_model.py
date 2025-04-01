from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from fastapi import UploadFile


# Response model for customer intent generation
class CustomerIntentResponse(BaseModel):
    """Response model for customer intent generation"""
    intent: str = Field(..., description="The generated customer intent statement")
    model: str = Field(..., description="Model used for generation")
    model_family: str = Field(..., description="Family of the model used (e.g., gpt-4, gpt-3.5-turbo)")
    capabilities: Dict[str, Any] = Field(..., description="Capabilities of the model used")
    usage: Dict[str, int] = Field(..., description="Token usage statistics")
    token_limit: int = Field(..., description="Maximum allowed tokens for the request")
    token_count: int = Field(..., description="Number of tokens in the processed text")
    remaining_tokens: int = Field(..., description="Remaining tokens available within the limit")
    text_used: str = Field(..., description="Text that was used to generate the intent")