import os
import tempfile
from typing import Optional
from fastapi import UploadFile
import aiofiles

class MarkdownServiceError(Exception):
    """Custom exception for Markdown service errors"""
    pass

class MarkdownService:
    """Service for processing markdown files"""
    
    def load_markdown_file(self, file_path: str) -> str:
        """
        Load markdown content from a file
        
        Args:
            file_path: Path to the markdown file
            
        Returns:
            String containing file contents
            
        Raises:
            MarkdownServiceError: If file cannot be read
        """
        try:
            if not os.path.exists(file_path):
                raise MarkdownServiceError(f"File not found: {file_path}")
                
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
            return content
        except Exception as e:
            if isinstance(e, MarkdownServiceError):
                raise
            raise MarkdownServiceError(f"Error reading markdown file: {str(e)}")
    
    async def process_uploaded_file(self, uploaded_file: UploadFile) -> str:
        """
        Process an uploaded markdown file
        
        Args:
            uploaded_file: Uploaded markdown file
            
        Returns:
            Processed markdown content with escapes
            
        Raises:
            MarkdownServiceError: If file processing fails
        """
        # Validate file type
        if not uploaded_file.filename.endswith(('.md', '.markdown')):
            raise MarkdownServiceError("Uploaded file must be a markdown file (.md, .markdown)")
        
        # Create temp file
        temp_dir = tempfile.TemporaryDirectory()
        temp_file_path = os.path.join(temp_dir.name, uploaded_file.filename)
        
        try:
            # Save uploaded file to temp location
            async with aiofiles.open(temp_file_path, 'wb') as out_file:
                content = await uploaded_file.read()
                await out_file.write(content)
            
            # Process file using existing method
            file_content = self.load_markdown_file(temp_file_path)
            return self.process_markdown(file_content)
        except Exception as e:
            if isinstance(e, MarkdownServiceError):
                raise
            raise MarkdownServiceError(f"Error processing uploaded file: {str(e)}")
        finally:
            # Clean up
            temp_dir.cleanup()
    
    def process_markdown(self, content: str) -> str:
        """
        Process markdown content for API response
        
        Args:
            content: Raw markdown content
            
        Returns:
            Processed markdown with escapes
            
        Raises:
            MarkdownServiceError: If processing fails
        """
        try:
            # Validate the content
            self.validate_markdown(content)
            
            # Escape the content for JSON response
            processed_content = self.escape_markdown(content)
            
            return processed_content
        except Exception as e:
            if isinstance(e, MarkdownServiceError):
                raise
            raise MarkdownServiceError(f"Error processing markdown: {str(e)}")
    
    def escape_markdown(self, content: str) -> str:
        """
        Escape markdown content for JSON response
        
        Args:
            content: Raw markdown content
            
        Returns:
            Escaped markdown string
        """
        # Replace newlines with \\n for JSON
        escaped = content.replace('\n', '\\n')
        
        return escaped
    
    def validate_markdown(self, content: Optional[str]) -> None:
        """
        Validate markdown content
        
        Args:
            content: Raw markdown content to validate
            
        Raises:
            MarkdownServiceError: If content is invalid
        """
        if content is None or content.strip() == '':
            raise MarkdownServiceError("Markdown content cannot be empty") 