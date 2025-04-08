from pydantic import BaseModel, Field
from typing import List, Dict, Any

class ContentTypeSelection(BaseModel):
    """Model for a selected content type"""
    type: str = Field(..., description="The content type (tutorial, how-to, explanation, reference)")
    confidence: float = Field(..., description="Confidence score for this selection")
    reasoning: str = Field(..., description="Reasoning for this selection")

class ContentTypeRequest(BaseModel):
    """Request model for content type selection"""
    intent: str = Field(..., description="The customer intent statement")
    text_used: str = Field(..., description="The source text to analyze")

class ContentTypeResponse(BaseModel):
    """Response model for content type selection"""
    selected_types: List[ContentTypeSelection] = Field(..., description="List of selected content types")
    model: str = Field(..., description="Model used for generation")
    model_family: str = Field(..., description="Family of the model used")
    capabilities: Dict[str, Any] = Field(..., description="Capabilities of the model used")
    usage: Dict[str, int] = Field(..., description="Token usage statistics")
    token_limit: int = Field(..., description="Maximum allowed tokens")
    token_count: int = Field(..., description="Number of tokens used")
    remaining_tokens: int = Field(..., description="Remaining tokens available") 