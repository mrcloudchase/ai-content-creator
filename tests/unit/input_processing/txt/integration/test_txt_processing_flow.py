import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import UploadFile
from app.input_processing.txt.services.txt_service import TxtService
from app.input_processing.core.services.input_processing_core_service import InputProcessingService

def test_txt_file_to_processed_text():
    """Test the flow from text file to processed text."""
    # Create a temporary text file
    with tempfile.NamedTemporaryFile(suffix='.txt', mode='w+', delete=False) as temp_file:
        temp_file.write("This is a test text file.\nWith multiple lines.\nFor testing purposes.")
        temp_file_path = temp_file.name
    
    try:
        # Create service instance
        service = TxtService()
        
        # Read the file
        raw_content = service.load_txt_file(temp_file_path)
        
        # Validate the content was read correctly
        assert "This is a test text file." in raw_content
        assert "With multiple lines." in raw_content
        assert "For testing purposes." in raw_content
        
        # Process the text content
        processed_content = service.process_txt(raw_content)
        
        # Verify the content was processed correctly
        assert "This is a test text file." in processed_content
        assert "With multiple lines." in processed_content
        assert "For testing purposes." in processed_content
    finally:
        # Clean up
        os.unlink(temp_file_path)

@pytest.mark.asyncio
async def test_txt_upload_flow():
    """Test the flow for processing an uploaded text file."""
    # Create mock UploadFile
    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "test.txt"
    
    # Create test content
    test_content = "This is a test text file.\nWith multiple lines.\nFor testing purposes."
    
    # Mock file reading
    mock_file.read = AsyncMock(return_value=test_content.encode('utf-8'))
    
    # Create a mock context manager for aiofiles.open
    mock_file_handle = MagicMock()
    mock_file_handle.__aenter__ = AsyncMock(return_value=mock_file_handle)
    mock_file_handle.__aexit__ = AsyncMock(return_value=None)
    mock_file_handle.write = AsyncMock()
    
    # Mock the file operations
    with patch('aiofiles.open', return_value=mock_file_handle):
        # Mock load_txt_file
        with patch.object(TxtService, 'load_txt_file', return_value=test_content):
            # Mock process_txt to use the actual implementation
            with patch.object(InputProcessingService, 'process_text', return_value="Processed: " + test_content) as mock_process:
                # Process the uploaded file
                service = TxtService()
                result = await service.process_uploaded_file(mock_file)
                
                # Verify the flow
                mock_file.read.assert_called_once()
                
                # Check that we got the processed result
                assert "Processed: " in result
                assert "This is a test text file." in result
                
                # Verify the process_text method was called
                mock_process.assert_called_once_with(test_content)

def test_txt_validation_flow():
    """Test the validation flow for text content."""
    # Valid content
    valid_content = "This is valid content."
    
    # Empty content
    empty_content = ""
    
    # Whitespace-only content
    whitespace_content = "   \n   "
    
    # Create service instance
    service = TxtService()
    
    # Test with valid content
    service.validate_txt(valid_content)
    
    # Test with invalid content - should raise exceptions
    with pytest.raises(Exception):
        service.validate_txt(empty_content)
    
    with pytest.raises(Exception):
        service.validate_txt(whitespace_content)
    
    with pytest.raises(Exception):
        service.validate_txt(None) 