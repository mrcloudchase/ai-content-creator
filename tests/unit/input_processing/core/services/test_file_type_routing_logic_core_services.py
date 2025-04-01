import pytest
from unittest.mock import MagicMock
from fastapi import UploadFile

from app.input_processing.core.services.file_handler_routing_logic_core_services import (
    FileHandlerRoutingService,
    FileHandlerRoutingError
)


class TestFileHandlerRoutingService:
    """Tests for the FileHandlerRoutingService class"""
    
    def test_get_file_extension(self):
        """Test file extension extraction"""
        service = FileHandlerRoutingService()
        
        # Test various file extensions
        assert service.get_file_extension("test.md") == ".md"
        assert service.get_file_extension("test.docx") == ".docx"
        assert service.get_file_extension("test.txt") == ".txt"
        assert service.get_file_extension("TEST.MD") == ".md"  # Tests case insensitivity
        assert service.get_file_extension("path/to/file.md") == ".md"  # Tests path handling
        
        # Test file with no extension
        assert service.get_file_extension("testfile") == ""
        
        # Test file with multiple dots
        assert service.get_file_extension("test.file.md") == ".md"
    
    def test_get_file_extension_empty_filename(self):
        """Test file extension extraction with empty filename"""
        service = FileHandlerRoutingService()
        
        with pytest.raises(FileHandlerRoutingError) as excinfo:
            service.get_file_extension("")
        
        assert "Filename cannot be empty" in str(excinfo.value)
    
    def test_get_file_type(self):
        """Test file type determination based on extension"""
        service = FileHandlerRoutingService()
        
        # Test supported file types
        assert service.get_file_type("test.md") == "markdown"
        assert service.get_file_type("test.markdown") == "markdown"
        assert service.get_file_type("test.docx") == "docx"
        assert service.get_file_type("test.doc") == "docx"
        assert service.get_file_type("test.txt") == "text"
        
        # Test case insensitivity
        assert service.get_file_type("TEST.MD") == "markdown"
        assert service.get_file_type("Test.Docx") == "docx"
    
    def test_get_file_type_unsupported(self):
        """Test file type determination with unsupported extension"""
        service = FileHandlerRoutingService()
        
        with pytest.raises(FileHandlerRoutingError) as excinfo:
            service.get_file_type("test.pdf")
        
        assert "Unsupported file type: .pdf" in str(excinfo.value)
    
    def test_validate_file_type(self):
        """Test file type validation"""
        service = FileHandlerRoutingService()
        
        # Create mock file objects
        md_file = MagicMock(spec=UploadFile)
        md_file.filename = "test.md"
        md_file.content_type = "text/markdown"
        
        docx_file = MagicMock(spec=UploadFile)
        docx_file.filename = "test.docx"
        docx_file.content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        
        txt_file = MagicMock(spec=UploadFile)
        txt_file.filename = "test.txt"
        txt_file.content_type = "text/plain"
        
        # Test validation with no allowed_types (should allow all supported types)
        assert service.validate_file_type(md_file) == "markdown"
        assert service.validate_file_type(docx_file) == "docx"
        assert service.validate_file_type(txt_file) == "text"
        
        # Test validation with specific allowed_types
        assert service.validate_file_type(md_file, ["markdown"]) == "markdown"
        assert service.validate_file_type(docx_file, ["docx", "markdown"]) == "docx"
        
        # Test validation with unsupported file type
        with pytest.raises(FileHandlerRoutingError) as excinfo:
            pdf_file = MagicMock(spec=UploadFile)
            pdf_file.filename = "test.pdf"
            pdf_file.content_type = "application/pdf"
            service.validate_file_type(pdf_file)
        
        assert "Unsupported file type" in str(excinfo.value)
        
        # Test validation with file type not in allowed_types
        with pytest.raises(FileHandlerRoutingError) as excinfo:
            service.validate_file_type(txt_file, ["markdown", "docx"])
        
        assert "File type 'text' is not allowed" in str(excinfo.value)
