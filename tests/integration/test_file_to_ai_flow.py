import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import tempfile
import os
from fastapi.testclient import TestClient
from app.main import app
from app.input_processing.markdown.services.markdown_service import MarkdownService
from app.input_processing.core.services.input_processing_core_service import InputProcessingService
from app.ai.core.services.tokenizer_core_service import TokenizerService
from app.ai.customer_intent.services.ai_customer_intent_service import CustomerIntentService
from app.ai.core.services.ai_core_service import AIService
from app.input_processing.docx.services.docx_service import DocxService

client = TestClient(app)

def test_markdown_to_tokens_flow():
    """Test the flow from markdown file to token count"""
    # Create a temporary markdown file
    with tempfile.NamedTemporaryFile(suffix='.md', mode='w+', delete=False) as temp_file:
        temp_file.write("# Test Markdown Document\n\nThis is a test paragraph for the integration test.")
        temp_file_path = temp_file.name
    
    try:
        # Process through the pipeline
        markdown_service = MarkdownService()
        raw_text = markdown_service.load_markdown_file(temp_file_path)
        
        # Process text using core service
        processed_text = InputProcessingService.process_text(raw_text)
        
        # Count tokens
        token_result = TokenizerService.count_tokens(processed_text)
        
        # Verify flow
        assert raw_text.startswith("# Test Markdown Document")
        assert "test paragraph" in processed_text
        assert token_result["token_count"] > 0
        assert token_result["model"] == "gpt-3.5-turbo"
        assert token_result["tokens_remaining"] > 0
    finally:
        # Clean up
        os.unlink(temp_file_path)

@pytest.mark.asyncio
async def test_text_to_customer_intent_flow():
    """Test the flow from text to customer intent"""
    # Sample text
    sample_text = "Feature request: User needs the ability to export data as CSV and PDF."
    
    # Mock AI service response
    mock_ai_response = {
        "text": "As a user, I want to export data in different formats because I need to use the information in other applications.",
        "model": "gpt-3.5-turbo",
        "usage": {"prompt_tokens": 20, "completion_tokens": 20, "total_tokens": 40}
    }
    
    # Create patched version of AIService
    with patch.object(AIService, 'generate_completion', new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = mock_ai_response
        
        # Process through services
        ai_service = AIService()
        customer_intent_service = CustomerIntentService(ai_service)
        
        # Count tokens
        token_result = TokenizerService.count_tokens(sample_text)
        
        # Generate customer intent
        intent_result = await customer_intent_service.generate_customer_intent(
            document_text=sample_text,
            user_type="user",
            max_tokens=100,
            temperature=0.5
        )
        
        # Verify flow
        assert token_result["token_count"] > 0
        assert "user" in intent_result["intent"].lower()
        assert "export" in intent_result["intent"].lower()
        assert intent_result["model"] == "gpt-3.5-turbo"
        
    # Verify the mock was called with the right parameters    
    mock_generate.assert_called_once()

@pytest.mark.asyncio
async def test_end_to_end_api_flow():
    """Test the end-to-end API flow with mocked AI service"""
    # Sample document text
    sample_text = "Feature request: User needs the ability to export data as CSV and PDF."
    
    # Mock AI service response
    mock_ai_response = {
        "text": "As a user, I want to export data in different formats because I need to use the information in other applications.",
        "model": "gpt-3.5-turbo",
        "usage": {"prompt_tokens": 20, "completion_tokens": 20, "total_tokens": 40}
    }
    
    # Create patched version of AIService
    with patch('app.ai.core.services.ai_core_service.AIService.generate_completion', new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = mock_ai_response
        
        # Make API request
        response = client.post(
            "/api/v1/customer-intent",
            json={
                "document_text": sample_text,
                "user_type": "user",
                "max_tokens": 100,
                "temperature": 0.5
            }
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert "intent" in data
        assert "export" in data["intent"].lower()
        assert data["model"] == "gpt-3.5-turbo"
        assert "usage" in data
        
    # Verify the mock was called with the right parameters
    mock_generate.assert_called_once()

@pytest.mark.asyncio
async def test_markdown_to_ai_flow():
    """Test the workflow from markdown file to AI completion."""
    # Create a temporary markdown file
    with tempfile.NamedTemporaryFile(suffix='.md', mode='w+', delete=False) as temp_file:
        temp_file.write("# Test Markdown\n\nThis is a test document for the AI flow.")
        temp_file_path = temp_file.name
    
    try:
        # Mock the AI service
        with patch('app.ai.core.services.ai_core_service.AIService.generate_completion', new_callable=AsyncMock) as mock_generate:
            # Configure mock response
            mock_generate.return_value = {
                "text": "As a user, I want to create documentation because it helps me understand the system.",
                "model": "gpt-3.5-turbo",
                "usage": {
                    "prompt_tokens": 30,
                    "completion_tokens": 20,
                    "total_tokens": 50
                }
            }
            
            # Test flow
            # Step 1: Read markdown file
            service = MarkdownService()
            content = service.load_markdown_file(temp_file_path)
            
            # Step 2: Process content
            processed_content = service.process_markdown(content)
            
            # Step 3: Count tokens
            token_result = TokenizerService.count_tokens(processed_content)
            
            # Step 4: Create AI service and generate completion
            ai_service = AIService()
            result = await ai_service.generate_completion(
                prompt=f"Generate customer intent based on: {processed_content}",
                max_tokens=150,
                temperature=0.5
            )
            
            # Step 5: Generate customer intent
            response_intent = client.post(
                "/api/v1/customer-intent",
                json={
                    "document_text": content,
                    "max_tokens": 150,
                    "temperature": 0.5
                }
            )
            
            # Verify flow
            assert "Test Markdown" in content
            assert "test document" in processed_content
            assert token_result["token_count"] > 0
            assert "documentation" in result["text"]
            assert "user" in result["text"]
            
            # Verify AI service was called correctly
            mock_generate.assert_called_once()
            call_args = mock_generate.call_args[1]
            assert "Test Markdown" in call_args["prompt"]
            assert call_args["max_tokens"] == 150
            assert call_args["temperature"] == 0.5
    finally:
        # Clean up
        os.unlink(temp_file_path)

def test_file_type_detection_to_processing_flow():
    """Test the workflow from file type detection to processing."""
    # Test with markdown
    with patch.object(MarkdownService, 'process_markdown', return_value="Processed markdown content"):
        # Read a markdown file
        markdown_content = "# Test Markdown\n\nThis is a test."
        
        # Process the content
        service = MarkdownService()
        result = service.process_markdown(markdown_content)
        
        # Verify
        assert result == "Processed markdown content"
    
    # Test with DOCX
    with patch.object(DocxService, 'extract_text', return_value="Processed DOCX content"):
        # Mock DOCX content
        docx_content = b'fake docx content'
        
        # Process content
        result = DocxService.extract_text(docx_content)
        
        # Verify
        assert result == "Processed DOCX content" 