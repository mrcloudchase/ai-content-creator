"""
Configuration file for pytest.
"""
import pytest
import os
import sys
from fastapi.testclient import TestClient
from app.main import app
from app.ai.core.services.ai_core_service import AIService
from app.ai.customer_intent.services.ai_customer_intent_service import CustomerIntentService

# Add asyncio marker to pytest
def pytest_configure(config):
    """Configure pytest with asyncio."""
    config.addinivalue_line(
        "markers", "asyncio: mark test as an asyncio test"
    )

@pytest.fixture
def test_client():
    """Return a test client for the FastAPI app."""
    return TestClient(app)

@pytest.fixture
def ai_service():
    """Return an AI service instance."""
    return AIService()

@pytest.fixture
def customer_intent_service(ai_service):
    """Return a customer intent service instance."""
    return CustomerIntentService(ai_service)

@pytest.fixture
def sample_markdown_text():
    """Return a sample markdown text for testing."""
    return """# Sample Markdown
    
This is a sample markdown document for testing.

## Features
- Feature 1
- Feature 2
- Feature 3
"""

@pytest.fixture
def sample_customer_intent_request():
    """Return a sample customer intent request with file data."""
    return {
        "filename": "test_document.md",
        "content": "Feature request: Allow users to export data to CSV",
        "content_type": "text/markdown"
    } 