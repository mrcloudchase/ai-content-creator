import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI
import io
import asyncio

from app.main import app
from app.config.settings import OpenAISettings
from app.ai.core.services.ai_core_service import AIService
from app.ai.core.services.tokenizer_core_service import TokenizerService
from app.input_processing.markdown.services.markdown_service import MarkdownService
from app.input_processing.docx.services.docx_service import DocxService
from app.input_processing.txt.services.txt_service import TxtService
from app.input_processing.core.services.file_handler_routing_logic_core_services import FileHandlerRoutingService
from app.ai.customer_intent.services.ai_customer_intent_service import CustomerIntentService


# Mock environment variables for testing
@pytest.fixture(scope="session", autouse=True)
def mock_env_vars():
    """Set mock environment variables for testing"""
    os.environ["OPENAI_API_KEY"] = "test-api-key"
    os.environ["OPENAI_DEFAULT_MODEL"] = "gpt-4"
    os.environ["OPENAI_ORGANIZATION"] = "test-org"
    

# OpenAI Settings fixture
@pytest.fixture
def openai_settings():
    """Return a configured OpenAISettings instance for testing"""
    settings = OpenAISettings(
        api_key="test-api-key",
        default_model="gpt-4-test",
        organization="test-org",
        temperature=0.5,
        max_tokens=100
    )
    return settings


# FastAPI test client
@pytest.fixture
def client():
    """Return a FastAPI TestClient instance"""
    return TestClient(app)


# Mock OpenAI Client Response
@pytest.fixture
def mock_openai_response():
    """Return a mock OpenAI completion response"""
    class MockChoice:
        def __init__(self):
            self.message = MagicMock()
            self.message.content = "As a content creator, I want to streamline my workflow because it saves time and increases productivity."

    class MockUsage:
        def __init__(self):
            self.prompt_tokens = 100
            self.completion_tokens = 50
            self.total_tokens = 150

    class MockResponse:
        def __init__(self):
            self.choices = [MockChoice()]
            self.model = "gpt-4-test"
            self.usage = MockUsage()

    return MockResponse()


# Mock AIService
@pytest.fixture
def mock_ai_service(mock_openai_response):
    """Return a mocked AIService instance"""
    with patch("app.ai.core.services.ai_core_service.openai.AsyncOpenAI") as mock_openai:
        # Setup the mock chat.completions.create method
        mock_client = MagicMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_openai_response)
        mock_openai.return_value = mock_client
        
        # Create the service with mock settings
        service = AIService(MagicMock())
        service.client = mock_client
        
        yield service


# Mock TokenizerService
@pytest.fixture
def mock_tokenizer_service():
    """Return a mocked TokenizerService instance"""
    service = MagicMock(spec=TokenizerService)
    service.validate_tokens.return_value = {
        "token_count": 100,
        "model_limit": 4096,
        "tokens_remaining": 3996,
        "percentage_used": 2.44,
        "model": "gpt-4-test",
        "model_family": "gpt",
        "capabilities": {"supports_functions": True, "supports_vision": False, "supports_embeddings": True},
        "encoding": "cl100k_base"
    }
    return service


# Mock CustomerIntentService
@pytest.fixture
def mock_customer_intent_service():
    """Return a mocked CustomerIntentService instance"""
    service = MagicMock(spec=CustomerIntentService)
    service.format_customer_intent_prompt.return_value = {
        "messages": [
            {"role": "system", "content": "You are an expert at analyzing documents..."},
            {"role": "user", "content": "Please analyze the following document and create a customer intent statement..."}
        ]
    }
    return service


# Test File Content
@pytest.fixture
def test_markdown_content():
    """Return test markdown content as bytes"""
    content = """# Test Document
    
## Introduction
This is a test document for our AI content creator.

## Customer Needs
- Need to simplify workflow
- Need to save time
- Need to improve productivity
    """
    return content.encode('utf-8')


@pytest.fixture
def test_docx_content():
    """Return a mock bytes object for docx testing"""
    # This is just a placeholder - real DOCX binary would be more complex
    return b'mock docx content'


@pytest.fixture
def test_txt_content():
    """Return test txt content as bytes"""
    content = """Test Document
    
Introduction
This is a test document for our AI content creator.

Customer Needs
- Need to simplify workflow
- Need to save time
- Need to improve productivity
    """
    return content.encode('utf-8')


# Mock file upload
@pytest.fixture
def mock_markdown_upload():
    """Create a mock markdown file upload"""
    file_content = """# Test Document
    
## Customer Needs
The customer needs a way to streamline their content creation workflow.
They want to save time and increase productivity.
    """
    
    class MockUpload:
        def __init__(self):
            self.filename = "test.md"
            self.content_type = "text/markdown"
            self._file = io.BytesIO(file_content.encode("utf-8"))
        
        async def read(self):
            return self._file.getvalue()
            
    return MockUpload()


@pytest.fixture
def mock_docx_upload():
    """Create a mock docx file upload"""
    # For testing purposes we're using dummy binary data
    file_content = b'mock docx binary content'
    
    class MockUpload:
        def __init__(self):
            self.filename = "test.docx"
            self.content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            self._file = io.BytesIO(file_content)
        
        async def read(self):
            return self._file.getvalue()
            
    return MockUpload()


@pytest.fixture
def mock_txt_upload():
    """Create a mock txt file upload"""
    file_content = """Test Document
    
Customer Needs
The customer needs a way to streamline their content creation workflow.
They want to save time and increase productivity.
    """
    
    class MockUpload:
        def __init__(self):
            self.filename = "test.txt"
            self.content_type = "text/plain"
            self._file = io.BytesIO(file_content.encode("utf-8"))
        
        async def read(self):
            return self._file.getvalue()
            
    return MockUpload()


# Mock file processing services
@pytest.fixture
def mock_markdown_service():
    """Return a mocked MarkdownService"""
    service = MagicMock(spec=MarkdownService)
    service.extract_text.return_value = "This is extracted markdown text for testing."
    return service


@pytest.fixture
def mock_docx_service():
    """Return a mocked DocxService"""
    service = MagicMock(spec=DocxService)
    service.extract_text.return_value = "This is extracted docx text for testing."
    return service


@pytest.fixture
def mock_txt_service():
    """Return a mocked TxtService"""
    service = MagicMock(spec=TxtService)
    service.extract_text.return_value = "This is extracted txt text for testing."
    return service


@pytest.fixture
def mock_file_handler_service():
    """Return a mocked FileHandlerRoutingService"""
    service = MagicMock(spec=FileHandlerRoutingService)
    service.validate_file_type.return_value = "markdown"  # Default to markdown
    return service
