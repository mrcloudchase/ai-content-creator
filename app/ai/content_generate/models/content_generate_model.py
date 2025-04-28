from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ContentTypeRequest(BaseModel):
    """Model representing a single content type request"""
    type: str = Field(..., description="The content type (tutorial, how-to, explanation, reference)")
    title: Optional[str] = Field(None, description="Optional title for the content")

class ContentGenerateRequest(BaseModel):
    """Request model for content generation"""
    intent: str = Field(..., description="The customer intent statement")
    text_used: str = Field(..., description="The source text to analyze")
    content_types: List[ContentTypeRequest] = Field(..., description="List of content types to generate")

class GeneratedContent(BaseModel):
    """Model representing a single piece of generated content"""
    type: str = Field(..., description="The content type (tutorial, how-to, explanation, reference)")
    title: str = Field(..., description="The title of the generated content")
    content: str = Field(..., description="The generated content in markdown format")

class ContentGenerateResponse(BaseModel):
    """Response model for content generation"""
    generated_content: List[GeneratedContent] = Field(..., description="List of generated content items")
    model: str = Field(..., description="Model used for generation")
    model_family: str = Field(..., description="Family of the model used")
    capabilities: Dict[str, Any] = Field(..., description="Capabilities of the model used")
    usage: Dict[str, int] = Field(..., description="Token usage statistics")
    token_limit: int = Field(..., description="Maximum allowed tokens")
    token_count: int = Field(..., description="Number of tokens used")
    remaining_tokens: int = Field(..., description="Remaining tokens available")
    text_used: str = Field(..., description="The text used for generation") 