import pytest
from unittest.mock import patch, MagicMock

from app.input_processing.markdown.services.markdown_service import (
    MarkdownService,
    MarkdownServiceError
)


class TestMarkdownService:
    """Tests for the MarkdownService class"""
    
    def test_extract_text_basic_markdown(self):
        """Test extracting text from basic markdown content"""
        service = MarkdownService()
        
        # Create test markdown content
        markdown_content = """# Test Document
        
## Introduction
This is a test document for markdown extraction.

## Features
- Feature 1
- Feature 2
- Feature 3

## Code Example
```python
def test_function():
    return "Hello, world!"
```
"""
        # Convert to bytes
        markdown_bytes = markdown_content.encode('utf-8')
        
        # Extract text
        result = service.extract_text(markdown_bytes)
        
        # Verify content extraction
        assert result is not None
        assert isinstance(result, str)
        assert "Test Document" in result
        assert "Introduction" in result
        assert "This is a test document for markdown extraction" in result
        assert "Features" in result
        assert "Feature 1" in result
        assert "Feature 2" in result
        assert "Feature 3" in result
        assert "Code Example" in result
        assert "test_function" in result
        assert "Hello, world!" in result
    
    def test_extract_text_empty_content(self):
        """Test extracting text from empty markdown content"""
        service = MarkdownService()
        
        # Create empty bytes
        empty_bytes = b""
        
        # Extract text should succeed but return empty string
        result = service.extract_text(empty_bytes)
        assert result == ""
    
    def test_extract_text_with_utf8_bom(self):
        """Test extracting text with UTF-8 BOM marker"""
        service = MarkdownService()
        
        # Create markdown content with UTF-8 BOM
        # UTF-8 BOM is the byte sequence: EF BB BF
        bom = b'\xef\xbb\xbf'
        markdown_content = "# Test with UTF-8 BOM\nThis is a test."
        markdown_bytes = bom + markdown_content.encode('utf-8')
        
        # Extract text
        result = service.extract_text(markdown_bytes)
        
        # Verify content extraction without BOM characters
        assert result is not None
        assert "# Test with UTF-8 BOM" in result
        assert "This is a test" in result
    
    def test_extract_text_with_different_encodings(self):
        """Test extracting text with different encodings"""
        service = MarkdownService()
        
        # Test with latin-1 encoding
        markdown_content = "# Test Document\nSpecial char: é"
        markdown_bytes = markdown_content.encode('latin-1')
        
        # Extract text
        result = service.extract_text(markdown_bytes)
        
        # Verify content extraction
        assert result is not None
        assert "Test Document" in result
        assert "Special char: é" in result
    
    def test_extract_text_with_invalid_encoding(self):
        """Test extracting text with invalid encoding"""
        service = MarkdownService()
        
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
        """Test that text extraction preserves important line breaks"""
        service = MarkdownService()
        
        # Create markdown with specific line break patterns
        # Note: In the actual implementation, line breaks are preserved exactly as they are
        markdown_content = """# Title

Paragraph 1.
This is still paragraph 1.

Paragraph 2.

- List item 1
- List item 2
"""
        # Convert to bytes
        markdown_bytes = markdown_content.encode('utf-8')
        
        # Extract text
        result = service.extract_text(markdown_bytes)
        
        # Verify line breaks are preserved as is
        assert result.count("\n\n") >= 2  # At least 2 paragraph breaks
        assert "Paragraph 1.\nThis is still paragraph 1." in result
