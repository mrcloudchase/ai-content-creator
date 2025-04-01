import logging
import traceback
from typing import Optional

# Set up module logger
logger = logging.getLogger(__name__)

class MarkdownServiceError(Exception):
    """
    Exception for Markdown service errors
    """
    pass

class MarkdownService:
    """
    Service for extracting text from markdown file
    """
    
    def extract_text(self, file_content: bytes) -> str:
        """
        Extract raw text from markdown file content
        
        Args:
            file_content: Binary content of the markdown file
            
        Returns:
            Raw text content from markdown file
            
        Raises:
            MarkdownServiceError: If text extraction fails
        """
        try:
            # Log start of processing
            logger.info("Starting Markdown text extraction")
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
                raise MarkdownServiceError("Failed to decode file content with any supported encoding")
            
            # Log content statistics
            lines = content.split('\n')
            logger.debug(f"Found {len(lines)} lines in markdown content")
            
            # Count markdown elements
            headers = sum(1 for line in lines if line.strip().startswith('#'))
            lists = sum(1 for line in lines if line.strip().startswith(('-', '*', '+')))
            code_blocks = sum(1 for line in lines if line.strip().startswith('```'))
            
            logger.debug(f"Markdown elements found: {headers} headers, {lists} lists, {code_blocks} code blocks")
            
            # Clean up content
            cleaned_text = content.strip()
            logger.info(f"Successfully extracted {len(cleaned_text)} characters from markdown content")
            
            return cleaned_text
            
        except Exception as e:
            logger.error(f"Error extracting text from Markdown: {str(e)}")
            logger.error(f"Error type: {type(e)}")
            logger.error(f"Error traceback: {traceback.format_exc()}")
            raise MarkdownServiceError(f"Error extracting text from markdown: {str(e)}")