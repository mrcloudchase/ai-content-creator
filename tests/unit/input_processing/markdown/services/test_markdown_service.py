import pytest
import os
import tempfile
from fastapi import UploadFile
from unittest.mock import AsyncMock, MagicMock, patch
from app.input_processing.markdown.services.markdown_service import MarkdownService, MarkdownServiceError
from app.input_processing.core.services.input_processing_core_service import InputProcessingService

def test_load_markdown_file():
    """Test loading markdown from a file."""
    # Create a temporary markdown file
    with tempfile.NamedTemporaryFile(suffix='.md', mode='w+', delete=False) as temp_file:
        temp_file.write("# Test Markdown\n\nThis is a test.")
        temp_file_path = temp_file.name
    
    try:
        # Test loading the file
        service = MarkdownService()
        content = service.load_markdown_file(temp_file_path)
        
        # Verify content
        assert "# Test Markdown" in content
        assert "This is a test." in content
        
        # Test with non-existent file
        with pytest.raises(MarkdownServiceError):
            service.load_markdown_file("non_existent_file.md")
    finally:
        # Clean up
        os.unlink(temp_file_path)

@pytest.mark.asyncio
async def test_process_uploaded_file():
    """Test processing an uploaded markdown file."""
    # Create a mock UploadFile
    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "test.md"
    
    # Create test content
    test_content = "# Test Markdown\n\nThis is a test."
    
    # Mock file read
    mock_file.read = AsyncMock(return_value=test_content.encode('utf-8'))
    
    # Mock aiofiles.open
    with patch('aiofiles.open', new_callable=AsyncMock) as mock_aio_open:
        # Mock file write
        mock_file_handle = AsyncMock()
        mock_file_handle.__aenter__.return_value = mock_file_handle
        mock_aio_open.return_value = mock_file_handle
        
        # Mock load_markdown_file to return our test content
        with patch.object(MarkdownService, 'load_markdown_file', return_value=test_content):
            # Mock process_markdown to return the processed content
            with patch.object(MarkdownService, 'process_markdown', return_value="Processed: " + test_content):
                # Test processing uploaded file
                service = MarkdownService()
                result = await service.process_uploaded_file(mock_file)
                
                # Verify result
                assert "Processed: " in result
                assert "# Test Markdown" in result
    
    # Test with invalid file type
    mock_file.filename = "test.txt"
    service = MarkdownService()
    with pytest.raises(MarkdownServiceError):
        await service.process_uploaded_file(mock_file)

def test_process_markdown():
    """Test processing markdown content."""
    # Mock InputProcessingService.process_text to return processed text
    with patch.object(InputProcessingService, 'process_text', return_value="Processed content"):
        service = MarkdownService()
        
        # Test with valid content
        result = service.process_markdown("# Test Markdown\n\nThis is a test.")
        assert result == "Processed content"
        
        # Test with invalid content
        with pytest.raises(MarkdownServiceError):
            service.process_markdown("")
    
    # Test error handling from InputProcessingService
    with patch.object(InputProcessingService, 'process_text', side_effect=Exception("Test error")):
        service = MarkdownService()
        with pytest.raises(MarkdownServiceError):
            service.process_markdown("# Test")

def test_validate_markdown():
    """Test validating markdown content."""
    service = MarkdownService()
    
    # Test with valid content
    service.validate_markdown("# Test Markdown")
    
    # Test with empty string
    with pytest.raises(MarkdownServiceError):
        service.validate_markdown("")
    
    # Test with None
    with pytest.raises(MarkdownServiceError):
        service.validate_markdown(None)
    
    # Test with whitespace only
    with pytest.raises(MarkdownServiceError):
        service.validate_markdown("   ") 