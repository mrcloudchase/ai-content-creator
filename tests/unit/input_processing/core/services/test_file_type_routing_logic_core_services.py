import pytest
from app.input_processing.core.services.file_handler_routing_logic_core_services import FileTypeRoutingService, FileTypeRoutingError
from fastapi import UploadFile
from unittest.mock import MagicMock

def test_get_file_extension():
    """Test getting file extension from filename."""
    # Test various file types
    assert FileTypeRoutingService.get_file_extension("test.md") == ".md"
    assert FileTypeRoutingService.get_file_extension("test.docx") == ".docx"
    assert FileTypeRoutingService.get_file_extension("test.txt") == ".txt"
    assert FileTypeRoutingService.get_file_extension("test.MD") == ".md"  # Test case insensitivity
    assert FileTypeRoutingService.get_file_extension("test.DOCX") == ".docx"  # Test case insensitivity
    
    # Test file with no extension
    assert FileTypeRoutingService.get_file_extension("test") == ""
    
    # Test file with multiple dots
    assert FileTypeRoutingService.get_file_extension("test.file.md") == ".md"
    
    # Test empty filename
    with pytest.raises(FileTypeRoutingError):
        FileTypeRoutingService.get_file_extension("")

def test_get_file_type():
    """Test determining file type based on extension."""
    # Test supported file types
    assert FileTypeRoutingService.get_file_type("test.md") == "markdown"
    assert FileTypeRoutingService.get_file_type("test.markdown") == "markdown"
    assert FileTypeRoutingService.get_file_type("test.docx") == "docx"
    assert FileTypeRoutingService.get_file_type("test.doc") == "docx"
    assert FileTypeRoutingService.get_file_type("test.txt") == "text"
    
    # Test case insensitivity
    assert FileTypeRoutingService.get_file_type("test.MD") == "markdown"
    assert FileTypeRoutingService.get_file_type("test.DOCX") == "docx"
    
    # Test unsupported file type
    with pytest.raises(FileTypeRoutingError):
        FileTypeRoutingService.get_file_type("test.pdf")

def test_validate_file_type():
    """Test validating file type against allowed types."""
    # Create mock UploadFile
    markdown_file = MagicMock(spec=UploadFile)
    markdown_file.filename = "test.md"
    
    docx_file = MagicMock(spec=UploadFile)
    docx_file.filename = "test.docx"
    
    pdf_file = MagicMock(spec=UploadFile)
    pdf_file.filename = "test.pdf"
    
    # Test with default allowed types (all supported types)
    assert FileTypeRoutingService.validate_file_type(markdown_file) == "markdown"
    assert FileTypeRoutingService.validate_file_type(docx_file) == "docx"
    
    # Test with specific allowed types
    assert FileTypeRoutingService.validate_file_type(markdown_file, ["markdown"]) == "markdown"
    assert FileTypeRoutingService.validate_file_type(docx_file, ["docx"]) == "docx"
    
    # Test with disallowed type
    with pytest.raises(FileTypeRoutingError):
        FileTypeRoutingService.validate_file_type(markdown_file, ["docx"])
    
    # Test with unsupported file type
    with pytest.raises(FileTypeRoutingError):
        FileTypeRoutingService.validate_file_type(pdf_file) 