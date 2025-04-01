import docx
import io
import logging
import traceback
from typing import Optional

# Set up module logger
logger = logging.getLogger(__name__)

class DocxServiceError(Exception):
    """Custom exception for document parsing errors"""
    pass

class DocxService:
    """Service for extracting text from .docx documents"""
    
    @staticmethod
    def extract_text(file_content: bytes) -> str:
        """
        Extract raw text from a .docx document
        
        Args:
            file_content: Binary content of the .docx file
            
        Returns:
            String containing all text from the document
            
        Raises:
            DocxServiceError: If there's an error reading the document
        """
        try:
            # Log start of processing
            logger.info("Starting DOCX text extraction")
            logger.debug(f"File content size: {len(file_content)} bytes")
            
            # Load the document from bytes
            doc = docx.Document(io.BytesIO(file_content))
            logger.debug("Successfully created DOCX document object")
            
            # Extract text from all paragraphs
            text_parts = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_parts.append(paragraph.text)
                    logger.debug(f"Processed paragraph: {len(paragraph.text)} chars")
            
            # Extract text from all tables
            for table in doc.tables:
                for row in table.rows:
                    row_texts = []
                    for cell in row.cells:
                        if cell.text.strip():
                            row_texts.append(cell.text.strip())
                    if row_texts:
                        text_parts.append(" | ".join(row_texts))
            
            # Join all text parts with newlines
            extracted_text = "\n".join(text_parts)
            logger.info(f"Successfully extracted {len(extracted_text)} characters from {len(text_parts)} paragraphs")
            
            # Log some statistics
            logger.debug(f"Number of paragraphs: {len(doc.paragraphs)}")
            logger.debug(f"Number of non-empty paragraphs: {len(text_parts)}")
            
            return extracted_text
            
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {str(e)}")
            logger.error(f"Error type: {type(e)}")
            logger.error(f"Error traceback: {traceback.format_exc()}")
            raise DocxServiceError(f"Error extracting text from document: {str(e)}") 