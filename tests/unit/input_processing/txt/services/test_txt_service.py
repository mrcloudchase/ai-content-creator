import pytest
from unittest.mock import patch, MagicMock

from app.input_processing.txt.services.txt_service import (
    TxtService,
    TxtServiceError
)


class TestTxtService:
    """Tests for the TxtService class"""
    
    def test_extract_text_basic(self):
        """Test basic text extraction from plain text file"""
        service = TxtService()
        
        # Create simple text content
        text_content = "This is a test plain text file.\nIt has multiple lines.\nIt should be extracted correctly."
        text_bytes = text_content.encode('utf-8')
        
        # Extract text
        result = service.extract_text(text_bytes)
        
        # Verify extraction
        assert result is not None
        assert isinstance(result, str)
        assert result == text_content.strip()
        assert "This is a test plain text file." in result
        assert "It has multiple lines." in result
        assert "It should be extracted correctly." in result
    
    def test_extract_text_empty_content(self):
        """Test extracting text from empty content"""
        service = TxtService()
        
        # Create empty bytes
        empty_bytes = b""
        
        # Extract text should succeed with empty string
        result = service.extract_text(empty_bytes)
        assert result == ""
    
    def test_extract_text_with_utf8_bom(self):
        """Test extracting text with UTF-8 BOM marker"""
        service = TxtService()
        
        # Create text content with UTF-8 BOM
        # UTF-8 BOM is the byte sequence: EF BB BF
        bom = b'\xef\xbb\xbf'
        text_content = "Text file with BOM\nSecond line"
        text_bytes = bom + text_content.encode('utf-8')
        
        # Extract text
        result = service.extract_text(text_bytes)
        
        # Verify content extraction without BOM characters
        assert result is not None
        assert "Text file with BOM" in result
        assert "Second line" in result
    
    def test_extract_text_with_different_encodings(self):
        """Test extracting text with different encodings"""
        service = TxtService()
        
        # Test with latin-1 encoding
        text_content = "Text with special char: é"
        text_bytes = text_content.encode('latin-1')
        
        # Extract text
        result = service.extract_text(text_bytes)
        
        # Verify content extraction
        assert result is not None
        assert "Text with special char: é" in result
    
    def test_extract_text_with_invalid_encoding(self):
        """Test extracting text with invalid encoding"""
        service = TxtService()
        
        # Create invalid bytes that can't be decoded with standard encodings
        invalid_bytes = b'\xC0\xC1\xF5\xF6'  # Invalid UTF-8 bytes
        
        # The test needs to be updated because latin-1 can actually decode any byte sequence
        # So the service will not raise an exception even with invalid UTF-8
        result = service.extract_text(invalid_bytes)
        
        # We should get some result using the latin-1 fallback
        assert result is not None
        assert isinstance(result, str)
        assert len(result) == len(invalid_bytes)  # Each byte becomes one character
    
    def test_extract_text_preserves_line_breaks(self):
        """Test that text extraction preserves line breaks"""
        service = TxtService()
        
        # Create text with specific line break patterns
        # The actual implementation strips the content so line count might be affected
        text_content = """Line 1
Line 2

Line 4 (after blank line)"""  # No trailing newline
        
        # Convert to bytes
        text_bytes = text_content.encode('utf-8')
        
        # Extract text
        result = service.extract_text(text_bytes)
        
        # Verify line breaks are preserved
        assert result.count("\n") == text_content.count("\n")  # Should have the same number of line breaks
        assert "Line 1\nLine 2" in result
        assert "Line 2\n\nLine 4" in result
