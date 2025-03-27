from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class CustomerIntentRequest(BaseModel):
    """Request model for generating a customer intent statement"""
    document_text: str = Field(..., description="The document text to base the customer intent on")
    user_type: Optional[str] = Field(None, description="Optional user type to focus on (e.g., 'network administrator', 'developer')")
    max_tokens: Optional[int] = Field(150, description="Maximum number of tokens to generate")
    temperature: Optional[float] = Field(0.5, description="Temperature for AI generation (0.0-1.0)")


class CustomerIntentResponse(BaseModel):
    """Response model for customer intent generation"""
    intent: str = Field(..., description="The generated customer intent statement")
    model: str = Field(..., description="Model used for generation")
    usage: Dict[str, Any] = Field(..., description="Token usage information") 