import pytest
from unittest.mock import patch, MagicMock
import io

from app.input_processing.core.services.file_handler_routing_logic_core_services import FileHandlerRoutingService
from app.input_processing.core.services.input_processing_core_service import InputProcessingService
from app.input_processing.markdown.services.markdown_service import MarkdownService
from app.input_processing.docx.services.docx_service import DocxService
from app.input_processing.txt.services.txt_service import TxtService


class TestCoreServicesIntegration:
    """Integration tests for input processing core services"""
    
    def test_file_handler_with_markdown_service(self, test_markdown_content):
        """Test integration between FileHandlerRoutingService and MarkdownService"""
        # Create services
        file_handler = FileHandlerRoutingService()
        markdown_service = MarkdownService()
        
        # Create a mock file upload
        mock_file = MagicMock()
        mock_file.filename = "test.md"
        mock_file.content_type = "text/markdown"
        
        # Test file type determination
        file_type = file_handler.get_file_type(mock_file.filename)
        assert file_type == "markdown"
        
        # Test file validation
        validated_type = file_handler.validate_file_type(mock_file)
        assert validated_type == "markdown"
        
        # Test content extraction
        extracted_text = markdown_service.extract_text(test_markdown_content)
        assert extracted_text is not None
        assert isinstance(extracted_text, str)
        assert "Test Document" in extracted_text
        
        # Test integrated flow
        file_type = file_handler.validate_file_type(mock_file)
        if file_type == "markdown":
            extracted_text = markdown_service.extract_text(test_markdown_content)
            assert extracted_text is not None
            assert "Introduction" in extracted_text
    
    def test_file_handler_with_docx_service(self, test_docx_content):
        """Test integration between FileHandlerRoutingService and DocxService"""
        # Create services
        file_handler = FileHandlerRoutingService()
        docx_service = DocxService()
        
        # Create a mock file upload
        mock_file = MagicMock()
        mock_file.filename = "test.docx"
        mock_file.content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        
        # Mock docx service to return test content
        with patch.object(docx_service, 'extract_text', return_value="Extracted DOCX content"):
            # Test file type determination
            file_type = file_handler.get_file_type(mock_file.filename)
            assert file_type == "docx"
            
            # Test file validation
            validated_type = file_handler.validate_file_type(mock_file)
            assert validated_type == "docx"
            
            # Test integrated flow
            file_type = file_handler.validate_file_type(mock_file)
            if file_type == "docx":
                extracted_text = docx_service.extract_text(test_docx_content)
                assert extracted_text == "Extracted DOCX content"
    
    def test_file_handler_with_txt_service(self, test_txt_content):
        """Test integration between FileHandlerRoutingService and TxtService"""
        # Create services
        file_handler = FileHandlerRoutingService()
        txt_service = TxtService()
        
        # Create a mock file upload
        mock_file = MagicMock()
        mock_file.filename = "test.txt"
        mock_file.content_type = "text/plain"
        
        # Test file type determination
        file_type = file_handler.get_file_type(mock_file.filename)
        assert file_type == "text"
        
        # Test file validation
        validated_type = file_handler.validate_file_type(mock_file)
        assert validated_type == "text"
        
        # Test content extraction
        extracted_text = txt_service.extract_text(test_txt_content)
        assert extracted_text is not None
        assert isinstance(extracted_text, str)
        assert "Test Document" in extracted_text
        
        # Test integrated flow
        file_type = file_handler.validate_file_type(mock_file)
        if file_type == "text":
            extracted_text = txt_service.extract_text(test_txt_content)
            assert extracted_text is not None
            assert "Customer Needs" in extracted_text
    
    def test_input_processing_with_extracted_content(self):
        """Test integration between file extraction and InputProcessingService"""
        # Create services
        markdown_service = MarkdownService()
        
        # Mock extracted content
        with patch.object(markdown_service, 'extract_text', return_value="# Test Document\n\nThis is test content."):
            # Extract text from mock file
            extracted_text = markdown_service.extract_text(b'mock content')
            
            # Process the extracted text
            processed_text = InputProcessingService.process_text(extracted_text)
            
            # Verify processed text
            assert processed_text is not None
            assert isinstance(processed_text, str)
            assert "Test Document" in processed_text
            assert "This is test content" in processed_text
    
    def test_complete_file_processing_pipeline(self):
        """Test the complete file processing pipeline"""
        # Create all services
        file_handler = FileHandlerRoutingService()
        markdown_service = MarkdownService()
        docx_service = DocxService()
        txt_service = TxtService()
        
        # Mock file uploads
        markdown_file = MagicMock()
        markdown_file.filename = "test.md"
        markdown_file.content_type = "text/markdown"
        
        docx_file = MagicMock()
        docx_file.filename = "test.docx"
        docx_file.content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        
        txt_file = MagicMock()
        txt_file.filename = "test.txt"
        txt_file.content_type = "text/plain"
        
        # Mock extracted content
        markdown_content = "# Markdown Document\n\nThis is markdown content."
        docx_content = "DOCX Document\n\nThis is DOCX content."
        txt_content = "TXT Document\n\nThis is TXT content."
        
        # Set up mocks
        with patch.object(markdown_service, 'extract_text', return_value=markdown_content), \
             patch.object(docx_service, 'extract_text', return_value=docx_content), \
             patch.object(txt_service, 'extract_text', return_value=txt_content):
            
            # Process markdown file
            file_type = file_handler.validate_file_type(markdown_file)
            assert file_type == "markdown"
            
            extracted_text = None
            if file_type == "markdown":
                extracted_text = markdown_service.extract_text(b'mock markdown content')
            elif file_type == "docx":
                extracted_text = docx_service.extract_text(b'mock docx content')
            elif file_type == "text":
                extracted_text = txt_service.extract_text(b'mock txt content')
            
            assert extracted_text == markdown_content
            
            # Process the extracted text
            processed_text = InputProcessingService.process_text(extracted_text)
            assert "Markdown Document" in processed_text
            
            # Repeat for DOCX file
            file_type = file_handler.validate_file_type(docx_file)
            assert file_type == "docx"
            
            extracted_text = None
            if file_type == "markdown":
                extracted_text = markdown_service.extract_text(b'mock markdown content')
            elif file_type == "docx":
                extracted_text = docx_service.extract_text(b'mock docx content')
            elif file_type == "text":
                extracted_text = txt_service.extract_text(b'mock txt content')
            
            assert extracted_text == docx_content
            
            # Process the extracted text
            processed_text = InputProcessingService.process_text(extracted_text)
            assert "DOCX Document" in processed_text
