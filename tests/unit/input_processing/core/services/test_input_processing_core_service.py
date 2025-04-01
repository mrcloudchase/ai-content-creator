import pytest
from app.input_processing.core.services.input_processing_core_service import InputProcessingService, InputProcessingError

def test_escape_special_chars():
    """Test escaping special characters for JSON compatibility."""
    # Test basic escaping
    assert InputProcessingService.escape_special_chars("Test\nNew Line") == "Test\nNew Line"
    assert InputProcessingService.escape_special_chars("Test\\Backslash") == "Test\\\\Backslash"
    
    # Test Unicode quotes and apostrophes
    assert InputProcessingService.escape_special_chars('Test "quotes" and \'apostrophes\'') == 'Test "quotes" and \'apostrophes\''
    
    # Test special characters
    assert InputProcessingService.escape_special_chars("Test dash—em dash") == "Test dash--em dash"
    assert InputProcessingService.escape_special_chars("Test…ellipsis") == "Test...ellipsis"
    
    # Test control characters
    control_chars = "".join(chr(i) for i in range(32) if i not in [9, 10, 13])  # Exclude tab, newline, return
    result = InputProcessingService.escape_special_chars(f"Test{control_chars}Control")
    assert result == "TestControl"  # Control characters should be removed
    
    # Test empty string
    assert InputProcessingService.escape_special_chars("") == ""
    assert InputProcessingService.escape_special_chars(None) == ""

def test_validate_text():
    """Test validating text content."""
    # Valid text
    InputProcessingService.validate_text("Valid text")
    
    # Empty text should raise error
    with pytest.raises(InputProcessingError):
        InputProcessingService.validate_text("")
    
    # None should raise error
    with pytest.raises(InputProcessingError):
        InputProcessingService.validate_text(None)
    
    # Whitespace only should raise error
    with pytest.raises(InputProcessingError):
        InputProcessingService.validate_text("   ")

def test_process_text():
    """Test processing raw text for API response."""
    # Test normal processing
    assert "processed text" in InputProcessingService.process_text("processed text")
    
    # Test processing with special characters
    processed = InputProcessingService.process_text('Text with "quotes" and \\ backslashes')
    assert "Text with" in processed
    assert "quotes" in processed
    assert "backslashes" in processed
    
    # Test error handling for empty text
    with pytest.raises(InputProcessingError):
        InputProcessingService.process_text("")
        
    # Test error handling for None
    with pytest.raises(InputProcessingError):
        InputProcessingService.process_text(None) 