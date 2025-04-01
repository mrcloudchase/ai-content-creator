import re
from typing import Optional, Dict

class InputProcessingError(Exception):
    """Custom exception for input processing errors"""
    pass

class InputProcessingService:
    """Service for processing text input and formatting"""
    
    # Constants for character handling
    CONTROL_CHARS_TO_KEEP = {'\t', '\n', '\r'}  # ASCII 9, 10, 13
    QUOTE_MAPPINGS: Dict[str, str] = {
        '"': '"', '"': '"',
        ''': "'", ''': "'"
    }
    SPECIAL_CHAR_MAPPINGS: Dict[str, str] = {
        '—': '--', '–': '-',
        '…': '...'
    }
    
    @staticmethod
    def normalize_line_breaks(text: str) -> str:
        """
        Normalize line breaks to \n
        """
        return text.replace('\r\n', '\n').replace('\r', '\n')
    
    @staticmethod
    def remove_control_chars(text: str) -> str:
        """
        Remove problematic control characters while preserving tabs and newlines
        """
        return re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """
        Normalize whitespace while preserving paragraph breaks
        """
        return re.sub(r' {2,}', ' ', text)
    
    @staticmethod
    def normalize_quotes(text: str) -> str:
        """
        Replace Unicode quotes and apostrophes with ASCII ones
        """
        for unicode_char, ascii_char in InputProcessingService.QUOTE_MAPPINGS.items():
            text = text.replace(unicode_char, ascii_char)
        return text
    
    @staticmethod
    def normalize_special_chars(text: str) -> str:
        """
        Replace other special characters with their ASCII equivalents
        """
        for unicode_char, ascii_char in InputProcessingService.SPECIAL_CHAR_MAPPINGS.items():
            text = text.replace(unicode_char, ascii_char)
        return text
    
    @staticmethod
    def escape_backslashes(text: str) -> str:
        """
        Escape backslashes for JSON response
        """
        return text.replace('\\', '\\\\')
    
    @staticmethod
    def sanitize_text(content: str) -> str:
        """
        Sanitize text for API response

        Args:
            content: Raw text content
            
        Returns:
            Sanitized text
        """
        if not content:
            return ""
            
        # Apply transformations in specific order
        text = InputProcessingService.normalize_line_breaks(content)
        text = InputProcessingService.remove_control_chars(text)
        text = InputProcessingService.normalize_whitespace(text)
        text = InputProcessingService.normalize_quotes(text)
        text = InputProcessingService.normalize_special_chars(text)
        text = InputProcessingService.escape_backslashes(text)
        
        return text
    
    @staticmethod
    def validate_text(content: Optional[str]) -> None:
        """
        Validate text content
        """
        if content is None or content.strip() == '':
            raise InputProcessingError("Content cannot be empty")
    
    @staticmethod
    def process_text(content: str) -> str:
        """
        Process raw text for API response

        Args:
            content: Raw text content
            
        Returns:
            Processed text
        """
        try:
            # Validate the content
            InputProcessingService.validate_text(content)
            
            # Escape the content for JSON response
            processed_content = InputProcessingService.sanitize_text(content)
            
            return processed_content
        except Exception as e:
            if isinstance(e, InputProcessingError):
                raise
            raise InputProcessingError(f"Error processing text: {str(e)}") 