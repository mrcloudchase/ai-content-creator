import pytest
from unittest.mock import patch, MagicMock
from app.input_processing.docx.services.docx_service import DocxService, TokenLimitError
from app.input_processing.core.services.input_processing_core_service import InputProcessingService
from app.ai.core.services.tokenizer_core_service import TokenizerService

SAMPLE_DOCX_CONTENT = b'sample docx binary content'

def test_docx_to_text_flow():
    """Test the flow from DOCX to extracted text."""
    # Mock docx.Document
    with patch('app.input_processing.docx.services.docx_service.docx.Document') as mock_document:
        # Configure mock document
        mock_doc = MagicMock()
        mock_document.return_value = mock_doc
        
        # Setup document structure for extraction
        mock_doc.element.body.iter.return_value = []  # No elements to process
        mock_doc.paragraphs = []
        mock_doc.tables = []
        
        # Mock input processing
        with patch.object(InputProcessingService, 'escape_special_chars', return_value="Processed content"):
            # Mock tokenizer
            with patch.object(TokenizerService, 'count_tokens') as mock_count_tokens:
                # Token count below limit
                mock_count_tokens.return_value = {
                    "token_count": 100,
                    "model": "gpt-3.5-turbo",
                    "model_limit": 4096,
                    "tokens_remaining": 3996
                }
                
                # Extract text
                result = DocxService.extract_text(SAMPLE_DOCX_CONTENT)
                
                # Verify flow
                mock_document.assert_called_once()
                mock_count_tokens.assert_called_once()
                
                # Check result
                assert result == "Processed content"

def test_docx_token_limit_flow():
    """Test the token limit check in the DOCX processing flow."""
    # Mock docx.Document
    with patch('app.input_processing.docx.services.docx_service.docx.Document'):
        # Mock input processing
        with patch.object(InputProcessingService, 'escape_special_chars', return_value="Processed content"):
            # Mock tokenizer to return count exceeding limit
            with patch.object(TokenizerService, 'count_tokens') as mock_count_tokens:
                # Token count above limit
                mock_count_tokens.return_value = {
                    "token_count": 10000,
                    "model": "gpt-3.5-turbo",
                    "model_limit": 4096,
                    "tokens_remaining": 0
                }
                
                # Extract text - should raise exception
                with pytest.raises(TokenLimitError):
                    DocxService.extract_text(SAMPLE_DOCX_CONTENT)
                
                # Verify tokenizer was called
                mock_count_tokens.assert_called_once()

def test_docx_parse_document_flow():
    """Test the flow for parsing a DOCX document into structured data."""
    # Mock docx.Document
    with patch('app.input_processing.docx.services.docx_service.docx.Document') as mock_document:
        # Configure mock document
        mock_doc = MagicMock()
        mock_document.return_value = mock_doc
        
        # Setup document elements
        mock_para = MagicMock()
        mock_para.text = "Sample paragraph"
        mock_para.style.name = "Normal"
        
        mock_heading = MagicMock()
        mock_heading.text = "Sample heading"
        mock_heading.style.name = "Heading 1"
        
        # Add to document
        mock_doc.paragraphs = [mock_para, mock_heading]
        mock_doc.tables = []
        
        # Mock core_properties
        mock_doc.core_properties.author = "Test Author"
        mock_doc.core_properties.created = "2023-01-01"
        mock_doc.core_properties.modified = "2023-01-02"
        mock_doc.core_properties.title = "Test Document"
        
        # Parse document
        result = DocxService.parse_document(SAMPLE_DOCX_CONTENT)
        
        # Verify flow
        mock_document.assert_called_once()
        
        # Check result structure
        assert "title" in result
        assert "paragraphs" in result
        assert "tables" in result
        assert "headings" in result
        assert "metadata" in result
        
        # Check content
        assert len(result["paragraphs"]) >= 1
        assert "Sample paragraph" in result["paragraphs"][0]["text"] 