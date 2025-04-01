import pytest
from unittest.mock import patch, MagicMock, mock_open
import io

from app.input_processing.docx.services.docx_service import (
    DocxService,
    DocxServiceError
)


class TestDocxService:
    """Tests for the DocxService class"""
    
    def test_extract_text_with_mock_docx(self):
        """Test text extraction from DOCX using mocked python-docx"""
        service = DocxService()
        
        # Mock document structure
        mock_paragraph1 = MagicMock()
        mock_paragraph1.text = "This is the first paragraph."
        
        mock_paragraph2 = MagicMock()
        mock_paragraph2.text = "This is the second paragraph."
        
        mock_doc = MagicMock()
        mock_doc.paragraphs = [mock_paragraph1, mock_paragraph2]
        mock_doc.tables = []
        
        # Mock the docx.Document class
        with patch("docx.Document", return_value=mock_doc):
            # Create test docx content (binary content doesn't matter as we're mocking)
            docx_bytes = b'mock docx binary content'
            
            # Extract text
            result = service.extract_text(docx_bytes)
            
            # Verify extraction
            assert result is not None
            assert isinstance(result, str)
            assert "This is the first paragraph." in result
            assert "This is the second paragraph." in result
    
    def test_extract_text_with_empty_document(self):
        """Test extracting text from empty document"""
        service = DocxService()
        
        # Mock empty document
        mock_doc = MagicMock()
        mock_doc.paragraphs = []
        mock_doc.tables = []
        
        # Mock the docx.Document class
        with patch("docx.Document", return_value=mock_doc):
            # Create test docx content
            docx_bytes = b'mock empty docx binary'
            
            # Extract text
            result = service.extract_text(docx_bytes)
            
            # Verify result is empty but not None
            assert result == ""
    
    def test_extract_text_document_error(self):
        """Test error handling when Document loading fails"""
        service = DocxService()
        
        # Mock Document class to raise an exception
        with patch("docx.Document", side_effect=Exception("Document error")):
            # Create test docx content
            docx_bytes = b'invalid docx content'
            
            # Extract text should raise DocxServiceError
            with pytest.raises(DocxServiceError) as excinfo:
                service.extract_text(docx_bytes)
            
            # Verify error message
            assert "Error extracting text from document" in str(excinfo.value)
            assert "Document error" in str(excinfo.value)
    
    def test_extract_text_with_complex_document(self):
        """Test text extraction from a more complex document"""
        service = DocxService()
        
        # Mock a document with various paragraph types
        mock_paragraphs = [
            MagicMock(text="Title"),
            MagicMock(text=""),  # Empty paragraph
            MagicMock(text="Normal paragraph with text."),
            MagicMock(text="Paragraph with special chars: ©®™"),
            MagicMock(text="                "),  # Whitespace paragraph
            MagicMock(text="Last paragraph.")
        ]
        
        mock_doc = MagicMock()
        mock_doc.paragraphs = mock_paragraphs
        mock_doc.tables = []
        
        # Mock the docx.Document class
        with patch("docx.Document", return_value=mock_doc):
            # Create test docx content
            docx_bytes = b'mock complex docx content'
            
            # Extract text
            result = service.extract_text(docx_bytes)
            
            # Verify content was correctly extracted and formatted
            assert "Title" in result
            assert "Normal paragraph with text" in result
            assert "Paragraph with special chars: ©®™" in result
            assert "Last paragraph" in result
    
    def test_extract_text_with_tables(self):
        """Test text extraction with tables (if supported)"""
        service = DocxService()
        
        # Mock document with paragraphs and tables
        mock_paragraphs = [
            MagicMock(text="Document with tables")
        ]
        
        # Mock a table with cells containing text
        mock_cell1 = MagicMock()
        mock_cell1.text = "Table cell 1"
        mock_cell2 = MagicMock()
        mock_cell2.text = "Table cell 2"
        
        mock_row = MagicMock()
        mock_row.cells = [mock_cell1, mock_cell2]
        
        mock_table = MagicMock()
        mock_table.rows = [mock_row]
        
        mock_doc = MagicMock()
        mock_doc.paragraphs = mock_paragraphs
        mock_doc.tables = [mock_table]
        
        # Mock the docx.Document class
        with patch("docx.Document", return_value=mock_doc):
            # Create test docx content
            docx_bytes = b'mock docx with tables'
            
            # Extract text
            result = service.extract_text(docx_bytes)
            
            # Verify paragraph content
            assert "Document with tables" in result
            
            # Verify table content (since we know the implementation supports tables)
            assert "Table cell 1 | Table cell 2" in result
    
    def test_file_io_handling(self):
        """Test that file IO is handled correctly"""
        service = DocxService()
        
        # Mock BytesIO and Document
        mock_bytes_io = MagicMock(spec=io.BytesIO)
        mock_doc = MagicMock()
        mock_doc.paragraphs = [MagicMock(text="Test paragraph")]
        mock_doc.tables = []
        
        with patch("io.BytesIO", return_value=mock_bytes_io) as mock_bytes_io_cls, \
             patch("docx.Document", return_value=mock_doc) as mock_document:
            
            # Create test docx content
            docx_bytes = b'mock docx content'
            
            # Extract text
            result = service.extract_text(docx_bytes)
            
            # Verify BytesIO was created with the content
            mock_bytes_io_cls.assert_called_once_with(docx_bytes)
            
            # Verify Document was created with the BytesIO object
            mock_document.assert_called_once_with(mock_bytes_io)
