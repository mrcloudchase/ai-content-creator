from pydantic import BaseModel, Field
from typing import Optional

class MarkdownParseRequest(BaseModel):
    """Request model for markdown parsing"""
    content: Optional[str] = Field(None, description="Raw markdown content to process")
    file_path: Optional[str] = Field(None, description="Path to markdown file to process")

    class Config:
        schema_extra = {
            "example": {
                "content": "# Sample Markdown\n\nThis is sample markdown content."
            }
        }

class MarkdownParseResponse(BaseModel):
    """Response model for markdown parsing"""
    document: str = Field(..., description="Processed markdown document with proper escaping") 