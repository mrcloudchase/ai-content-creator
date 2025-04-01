import logging
import traceback
from typing import Optional

# Set up module logger
logger = logging.getLogger(__name__)

class TxtServiceError(Exception):
    """Custom exception for TXT service errors"""
    pass

class TxtService:
    """Service for extracting text from plain text files"""
    
    def extract_text(self, file_content: bytes) -> str:
        """
        Extract raw text from text file content
        
        Args:
            file_content: Binary content of the text file
            
        Returns:
            Raw text content from the file
            
        Raises:
            TxtServiceError: If text extraction fails
        """
        try:
            # Log start of processing
            logger.info("Starting text file extraction")
            logger.debug(f"File content size: {len(file_content)} bytes")
            
            # Try different encodings in order of preference
            encodings = ['utf-8', 'utf-8-sig', 'latin-1']
            content = None
            
            for encoding in encodings:
                try:
                    content = file_content.decode(encoding)
                    logger.debug(f"Successfully decoded file content as {encoding}")
                    break
                except UnicodeDecodeError as e:
                    logger.warning(f"{encoding} decode failed: {str(e)}")
                    continue
            
            if content is None:
                raise TxtServiceError("Failed to decode file content with any supported encoding")
            
            # Log content statistics
            lines = content.split('\n')
            logger.debug(f"Found {len(lines)} lines in text content")
            
            # Clean up content
            cleaned_text = content.strip()
            logger.info(f"Successfully extracted {len(cleaned_text)} characters from text content")
            
            return cleaned_text
            
        except Exception as e:
            logger.error(f"Error extracting text from file: {str(e)}")
            logger.error(f"Error type: {type(e)}")
            logger.error(f"Error traceback: {traceback.format_exc()}")
            raise TxtServiceError(f"Error extracting text from file: {str(e)}") 