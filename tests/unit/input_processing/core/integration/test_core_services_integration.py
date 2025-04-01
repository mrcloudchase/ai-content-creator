import pytest
from fastapi import UploadFile
from unittest.mock import MagicMock
from app.input_processing.core.services.file_handler_routing_logic_core_services import FileTypeRoutingService
from app.input_processing.core.services.input_processing_core_service import InputProcessingService

def test_file_routing_and_processing_integration():
    """
    Test integration between file type routing and input processing.
    This tests the flow for determining file type and processing its content.
    """
    # Test data
    test_text = 'Text with special characters: "quotes" and \\ backslashes'
    
    # Create mock uploaded files with different extensions
    markdown_file = MagicMock(spec=UploadFile)
    markdown_file.filename = "test.md"
    
    docx_file = MagicMock(spec=UploadFile)
    docx_file.filename = "test.docx"
    
    txt_file = MagicMock(spec=UploadFile)
    txt_file.filename = "test.txt"
    
    # Step 1: Determine file type
    md_type = FileTypeRoutingService.validate_file_type(markdown_file)
    docx_type = FileTypeRoutingService.validate_file_type(docx_file)
    txt_type = FileTypeRoutingService.validate_file_type(txt_file)
    
    # Verify file types
    assert md_type == "markdown"
    assert docx_type == "docx"
    assert txt_type == "text"
    
    # Step 2: Process content based on file type
    processed_text = InputProcessingService.process_text(test_text)
    
    # Verify text processing
    assert 'Text with special characters' in processed_text
    assert 'quotes' in processed_text
    assert 'backslashes' in processed_text
    
    # Check that backslashes are properly escaped
    assert processed_text.count('\\') > test_text.count('\\')

def test_routing_logic_with_allowed_types():
    """Test routing logic with filtered allowed types."""
    # Create mock uploaded files
    markdown_file = MagicMock(spec=UploadFile)
    markdown_file.filename = "test.md"
    
    docx_file = MagicMock(spec=UploadFile)
    docx_file.filename = "test.docx"
    
    # Define allowed types for different scenarios
    markdown_only = ["markdown"]
    docx_only = ["docx"]
    both_types = ["markdown", "docx"]
    
    # Test with markdown file
    assert FileTypeRoutingService.validate_file_type(markdown_file, markdown_only) == "markdown"
    assert FileTypeRoutingService.validate_file_type(markdown_file, both_types) == "markdown"
    
    with pytest.raises(Exception):
        FileTypeRoutingService.validate_file_type(markdown_file, docx_only)
    
    # Test with docx file
    assert FileTypeRoutingService.validate_file_type(docx_file, docx_only) == "docx"
    assert FileTypeRoutingService.validate_file_type(docx_file, both_types) == "docx"
    
    with pytest.raises(Exception):
        FileTypeRoutingService.validate_file_type(docx_file, markdown_only) 