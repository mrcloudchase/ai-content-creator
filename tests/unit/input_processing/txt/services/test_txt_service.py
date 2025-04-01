import pytest
import os
import tempfile
from fastapi import UploadFile
from unittest.mock import AsyncMock, MagicMock, patch
from app.input_processing.txt.services.txt_service import TxtService, TxtServiceError
from app.input_processing.core.services.input_processing_core_service import InputProcessingService

def test_load_txt_file():
    """Test loading text from a file."""
    # Create a temporary text file
    with tempfile.NamedTemporaryFile(suffix='.txt', mode='w+', delete=False) as temp_file:
        temp_file.write("This is a test text file.\nSecond line.")
        temp_file_path = temp_file.name
    
    try:
        # Test loading the file
        service = TxtService()
        content = service.load_txt_file(temp_file_path)
        
        # Verify content
        assert "This is a test text file." in content
        assert "Second line." in content
        
        # Test with non-existent file
        with pytest.raises(TxtServiceError):
            service.load_txt_file("non_existent_file.txt")
    finally:
        # Clean up
        os.unlink(temp_file_path)

@pytest.mark.asyncio
async def test_process_uploaded_file():
    """Test processing an uploaded text file."""
    # Create a mock UploadFile
    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "test.txt"
    
    # Create test content
    test_content = "This is a test text file.\nSecond line."
    
    # Mock file read
    mock_file.read = AsyncMock(return_value=test_content.encode('utf-8'))
    
    # Create a mock context manager for aiofiles.open
    mock_file_handle = MagicMock()
    mock_file_handle.__aenter__ = AsyncMock(return_value=mock_file_handle)
    mock_file_handle.__aexit__ = AsyncMock(return_value=None)
    mock_file_handle.write = AsyncMock()
    
    # Mock aiofiles.open to return our mock file handle
    with patch('aiofiles.open', return_value=mock_file_handle):
        # Mock load_txt_file
        with patch.object(TxtService, 'load_txt_file', return_value=test_content):
            # Mock process_txt
            with patch.object(TxtService, 'process_txt', return_value="Processed: " + test_content):
                # Test processing uploaded file
                service = TxtService()
                result = await service.process_uploaded_file(mock_file)
                
                # Verify result
                assert "Processed: " in result
                assert "This is a test text file." in result
    
    # Test with invalid file type
    mock_file.filename = "test.md"
    service = TxtService()
    with pytest.raises(TxtServiceError):
        await service.process_uploaded_file(mock_file)

def test_process_txt():
    """Test processing text content."""
    # Mock InputProcessingService.process_text to return processed text
    with patch.object(InputProcessingService, 'process_text', return_value="Processed content"):
        service = TxtService()
        
        # Test with valid content
        result = service.process_txt("This is a test text file.\nSecond line.")
        assert result == "Processed content"
        
        # Test with invalid content
        with pytest.raises(TxtServiceError):
            service.process_txt("")
    
    # Test error handling from InputProcessingService
    with patch.object(InputProcessingService, 'process_text', side_effect=Exception("Test error")):
        service = TxtService()
        with pytest.raises(TxtServiceError):
            service.process_txt("Test text")

def test_validate_txt():
    """Test validating text content."""
    service = TxtService()
    
    # Test with valid content
    service.validate_txt("Test text")
    
    # Test with empty string
    with pytest.raises(TxtServiceError):
        service.validate_txt("")
    
    # Test with None
    with pytest.raises(TxtServiceError):
        service.validate_txt(None)
    
    # Test with whitespace only
    with pytest.raises(TxtServiceError):
        service.validate_txt("   ") 