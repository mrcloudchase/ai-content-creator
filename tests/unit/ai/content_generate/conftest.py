import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from app.ai.content_generate.services.content_generate_service import ContentGenerateService
from app.ai.content_generate.models.content_generate_model import (
    ContentTypeRequest,
    ContentGenerateRequest,
    GeneratedContent,
    ContentGenerateResponse
)

@pytest.fixture
def content_generate_service():
    """Return a ContentGenerateService instance"""
    return ContentGenerateService()

@pytest.fixture
def mock_content_prompt():
    """Return a mock content generation prompt"""
    return {
        "messages": [
            {
                "role": "system",
                "content": "You are an AI content creation assistant specialized in creating Tutorial content."
            },
            {
                "role": "user", 
                "content": "Customer Intent: As a developer, I want to learn FastAPI.\n\nPlease create a tutorial."
            }
        ]
    }

@pytest.fixture
def mock_ai_completion():
    """Return a mock AI completion response"""
    return {
        "text": "# Getting Started with FastAPI\n\nThis is a tutorial on FastAPI.",
        "model": "gpt-4",
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150
        }
    }

@pytest.fixture
def mock_token_info():
    """Return mock token information"""
    return {
        "model": "gpt-4",
        "model_family": "gpt",
        "capabilities": {"supports_functions": True},
        "usage": {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150},
        "model_limit": 4000,
        "token_count": 1000,
        "tokens_remaining": 3000,
        "percentage_used": 25
    }

@pytest.fixture
def sample_content_request():
    """Return a sample content generation request"""
    return ContentGenerateRequest(
        intent="As a developer, I want to learn FastAPI because it's a modern API framework.",
        text_used="FastAPI is a modern, fast (high-performance), web framework for building APIs with Python.",
        content_types=[
            ContentTypeRequest(type="tutorial", title="Getting Started with FastAPI"),
            ContentTypeRequest(type="how-to", title=None)
        ]
    )

@pytest.fixture
def sample_generated_content():
    """Return sample generated content items"""
    return [
        GeneratedContent(
            type="tutorial",
            title="Getting Started with FastAPI",
            content="# Getting Started with FastAPI\n\nThis is a tutorial on FastAPI."
        ),
        GeneratedContent(
            type="how-to",
            title="How to Build an API with FastAPI",
            content="# How to Build an API with FastAPI\n\nFollow these steps to build an API."
        )
    ] 