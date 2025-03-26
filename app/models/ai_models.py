from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class AIPromptRequest(BaseModel):
    """Request model for AI prompt"""
    prompt: str = Field(..., description="The prompt to send to the AI")
    model: Optional[str] = Field(None, description="The model to use (defaults to configured model)")
    max_tokens: Optional[int] = Field(None, description="Maximum number of tokens to generate")
    temperature: Optional[float] = Field(None, description="Sampling temperature for generation")

class AIUsage(BaseModel):
    """Model for token usage statistics"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class AIResponse(BaseModel):
    """Response model for AI completions"""
    text: str = Field(..., description="The generated text response")
    model: str = Field(..., description="The model used for generation")
    usage: AIUsage = Field(..., description="Token usage statistics") 