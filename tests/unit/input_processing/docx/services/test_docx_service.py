import pytest
import io
from unittest.mock import patch, MagicMock
from app.input_processing.docx.services.docx_service import DocxService, DocxServiceError, TokenLimitError
from app.input_processing.core.services.input_processing_core_service import InputProcessingService
from app.ai.core.services.tokenizer_core_service import TokenizerService

# Sample binary content for testing
SAMPLE_DOCX_CONTENT = b'sample docx content'

def test_parse_document():
    """Test parsing a docx document."""
    # Mock docx.Document
    with patch('app.input_processing.docx.services.docx_service.docx') as mock_docx:
        # Configure mock document
        mock_doc = MagicMock()
        mock_docx.Document.return_value = mock_doc
        
        # Mock document properties
        mock_doc.paragraphs = [MagicMock()]
        mock_doc.paragraphs[0].text = "Test Document"
        
        # Mock BytesIO
        with patch('app.input_processing.docx.services.docx_service.io.BytesIO') as mock_bytesio:
            mock_bytesio.return_value = "mock_bytes_io"
            
            # Test with valid content
            result = DocxService.parse_document(SAMPLE_DOCX_CONTENT)
            
            # Verify BytesIO was called with content
            mock_bytesio.assert_called_once_with(SAMPLE_DOCX_CONTENT)
            
            # Verify Document was created with BytesIO result
            mock_docx.Document.assert_called_once_with("mock_bytes_io")
            
            # Verify result structure
            assert "title" in result
            assert "paragraphs" in result
            assert "tables" in result
            assert "headings" in result
            assert "metadata" in result
    
    # Test with empty content
    with pytest.raises(AssertionError):
        DocxService.parse_document(b'')
    
    # Test with None content
    with pytest.raises(AssertionError):
        DocxService.parse_document(None)
    
    # Test with non-bytes content
    with pytest.raises(AssertionError):
        DocxService.parse_document("string content")

def test_extract_text():
    """Test extracting text from a docx document."""
    # Mock docx.Document
    with patch('app.input_processing.docx.services.docx_service.docx') as mock_docx:
        # Configure mock document
        mock_doc = MagicMock()
        mock_docx.Document.return_value = mock_doc
        
        # Mock document content
        mock_doc.element.body.iter.return_value = []  # No elements to process
        mock_doc.paragraphs = []
        mock_doc.tables = []
        
        # Mock InputProcessingService
        with patch.object(InputProcessingService, 'escape_special_chars', return_value="Processed content"):
            # Mock TokenizerService
            with patch.object(TokenizerService, 'count_tokens') as mock_count_tokens:
                # Configure token count to be under limit
                mock_count_tokens.return_value = {
                    "token_count": 100,
                    "model": "gpt-3.5-turbo",
                    "model_limit": 4096,
                    "tokens_remaining": 3996
                }
                
                # Test with valid content
                result = DocxService.extract_text(SAMPLE_DOCX_CONTENT)
                
                # Verify result is a string
                assert isinstance(result, str)
                assert result == "Processed content"
    
    # Test token limit exceeded
    with patch('app.input_processing.docx.services.docx_service.docx'):
        with patch.object(InputProcessingService, 'escape_special_chars', return_value="Content"):
            with patch.object(TokenizerService, 'count_tokens') as mock_count_tokens:
                # Configure token count to exceed limit
                mock_count_tokens.return_value = {
                    "token_count": 10000,
                    "model": "gpt-3.5-turbo",
                    "model_limit": 4096,
                    "tokens_remaining": 0
                }
                
                # Test token limit exceeded
                with pytest.raises(TokenLimitError):
                    DocxService.extract_text(SAMPLE_DOCX_CONTENT)

def test_get_title():
    """Test getting title from document."""
    # Create mock document
    mock_doc = MagicMock()
    
    # Test with paragraphs
    mock_doc.paragraphs = [MagicMock()]
    mock_doc.paragraphs[0].text = "Document Title"
    
    title = DocxService._get_title(mock_doc)
    assert title == "Document Title"
    
    # Test with empty paragraphs
    mock_doc.paragraphs = []
    title = DocxService._get_title(mock_doc)
    assert title == "Untitled Document"
    
    # Test with empty text in first paragraph
    mock_doc.paragraphs = [MagicMock()]
    mock_doc.paragraphs[0].text = "  "
    
    title = DocxService._get_title(mock_doc)
    assert title == "Untitled Document"

def test_get_paragraphs():
    """Test getting paragraphs from document."""
    # Create mock document
    mock_doc = MagicMock()
    
    # Test with paragraphs
    mock_para1 = MagicMock()
    mock_para1.text = "Paragraph 1"
    mock_para1.style.name = "Normal"
    
    mock_para2 = MagicMock()
    mock_para2.text = "Paragraph 2"
    mock_para2.style.name = "Heading 1"
    
    mock_doc.paragraphs = [mock_para1, mock_para2]
    
    paragraphs = DocxService._get_paragraphs(mock_doc)
    assert len(paragraphs) == 2
    assert paragraphs[0]["text"] == "Paragraph 1"
    assert paragraphs[0]["style"] == "Normal"
    assert paragraphs[1]["text"] == "Paragraph 2"
    assert paragraphs[1]["style"] == "Heading 1" 