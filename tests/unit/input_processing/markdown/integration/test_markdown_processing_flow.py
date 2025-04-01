import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import UploadFile
from app.input_processing.markdown.services.markdown_service import MarkdownService
from app.input_processing.core.services.input_processing_core_service import InputProcessingService

def test_markdown_file_to_processed_text():
    """Test the flow from markdown file to processed text."""
    # Create a temporary markdown file
    with tempfile.NamedTemporaryFile(suffix='.md', mode='w+', delete=False) as temp_file:
        temp_file.write("# Test Markdown\n\nThis is a **test** with some _formatting_.")
        temp_file_path = temp_file.name
    
    try:
        # Create service instance
        service = MarkdownService()
        
        # Read the file
        raw_content = service.load_markdown_file(temp_file_path)
        
        # Validate the content was read correctly
        assert "# Test Markdown" in raw_content
        assert "**test**" in raw_content
        assert "_formatting_" in raw_content
        
        # Process the markdown content
        processed_content = service.process_markdown(raw_content)
        
        # Verify the content was processed correctly
        assert "Test Markdown" in processed_content
        assert "test" in processed_content
        assert "formatting" in processed_content
    finally:
        # Clean up
        os.unlink(temp_file_path)

@pytest.mark.asyncio
async def test_markdown_upload_flow():
    """Test the flow for processing an uploaded markdown file."""
    # Create mock UploadFile
    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "test.md"
    
    # Create test content
    test_content = "# Test Markdown\n\nThis is a **test** document."
    
    # Mock file reading
    mock_file.read = AsyncMock(return_value=test_content.encode('utf-8'))
    
    # Mock the file operations
    with patch('aiofiles.open', new_callable=AsyncMock) as mock_open:
        # Create mock file handle
        mock_handle = AsyncMock()
        mock_handle.__aenter__.return_value = mock_handle
        mock_open.return_value = mock_handle
        
        # Mock load_markdown_file
        with patch.object(MarkdownService, 'load_markdown_file', return_value=test_content):
            # Mock process_markdown to use the actual implementation
            with patch.object(InputProcessingService, 'process_text', return_value="Processed: " + test_content) as mock_process:
                # Process the uploaded file
                service = MarkdownService()
                result = await service.process_uploaded_file(mock_file)
                
                # Verify the flow
                mock_file.read.assert_called_once()
                mock_open.assert_called_once()
                
                # Check that we got the processed result
                assert "Processed: " in result
                assert "Test Markdown" in result
                
                # Verify the process_text method was called
                mock_process.assert_called_once_with(test_content)

def test_markdown_validation_flow():
    """Test the validation flow for markdown content."""
    # Valid content
    valid_content = "# Valid Markdown\n\nThis is valid content."
    
    # Empty content
    empty_content = ""
    
    # Whitespace-only content
    whitespace_content = "   \n   "
    
    # Create service instance
    service = MarkdownService()
    
    # Test with valid content
    service.validate_markdown(valid_content)
    
    # Test with invalid content - should raise exceptions
    with pytest.raises(Exception):
        service.validate_markdown(empty_content)
    
    with pytest.raises(Exception):
        service.validate_markdown(whitespace_content)
    
    with pytest.raises(Exception):
        service.validate_markdown(None) 