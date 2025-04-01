import os
from typing import Optional
from fastapi import UploadFile
import logging
import traceback

# Set up module logger
logger = logging.getLogger(__name__)

class FileHandlerRoutingError(Exception):
    """
    Exception for file type routing errors
    """
    pass

class FileHandlerRoutingService:
    """
    Service for determining file type and routing processing based on file extension
    """

    # Dictionary mapping file extensions to their types
    FILE_EXTENSIONS_DICT = {
        # Markdown files
        ".md": "markdown",
        ".markdown": "markdown",
        
        # Word documents
        ".docx": "docx",
        ".doc": "docx",
        
        # Text files
        ".txt": "text",
    }
    
    @staticmethod
    def get_file_extension(filename: str) -> str:
        """
        Get file extension from filename

        Args:
            filename: Filename to get extension from
            
        Returns:
            File extension with leading dot

        Raises:
            FileHandlerRoutingError: If filename is empty
        """
        if not filename:
            raise FileHandlerRoutingError("Filename cannot be empty")
            
        _, ext = os.path.splitext(filename.lower())
        return ext
    
    @staticmethod
    def get_file_type(filename: str) -> str:
        """
        Get file type based on extension

        Args:
            filename: Filename to get type from
            
        Returns:
            File type
            
        Raises:
            FileHandlerRoutingError: If file type is not supported
        """
        ext = FileHandlerRoutingService.get_file_extension(filename)
        
        file_type = FileHandlerRoutingService.FILE_EXTENSIONS_DICT.get(ext)

        if not file_type:
            raise FileHandlerRoutingError(f"Unsupported file type: {ext}")
            
        return file_type
    
    @staticmethod
    def validate_file_type(uploaded_file: UploadFile, allowed_types: Optional[list] = None) -> str:
        """
        Validate file type against allowed types
        
        Args:
            uploaded_file: Uploaded file to validate
            allowed_types: List of allowed file types
            
        Returns:
            Determined file type if valid
            
        Raises:
            FileHandlerRoutingError: If file type is not allowed
        """
        try:
            # Log file details
            logger.info(f"Processing file: {uploaded_file.filename} (content_type: {uploaded_file.content_type})")
            
            if allowed_types is None:
                allowed_types = list(set(FileHandlerRoutingService.FILE_EXTENSIONS_DICT.values()))
                
            file_type = FileHandlerRoutingService.get_file_type(uploaded_file.filename)
            
            if file_type not in allowed_types:
                allowed_types_str = ", ".join(allowed_types)
                error_msg = f"File type '{file_type}' is not allowed. Allowed types: {allowed_types_str}"
                logger.error(error_msg)
                raise FileHandlerRoutingError(error_msg)
                
            logger.info(f"Processing file of type: {file_type}")
            return file_type
            
        except Exception as e:
            logger.error(f"Error validating file type: {str(e)}")
            logger.error(f"Error type: {type(e)}")
            logger.error(f"Error traceback: {traceback.format_exc()}")
            raise FileHandlerRoutingError(f"Error validating file type: {str(e)}")