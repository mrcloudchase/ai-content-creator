from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Form
from app.models.markdown_models import MarkdownParseResponse
from app.services.markdown_service import MarkdownService, MarkdownServiceError
import logging
from typing import Optional

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/markdown",
    tags=["markdown"],
)

def get_markdown_service():
    """Dependency to get Markdown service instance"""
    return MarkdownService()

@router.post("/parse", response_model=MarkdownParseResponse)
async def parse_markdown(
    file: UploadFile = File(None),
    content: Optional[str] = Form(None),
    file_path: Optional[str] = Form(None),
    service: MarkdownService = Depends(get_markdown_service)
):
    """
    Parse and process markdown content for LLM input
    
    - **file**: Markdown file to upload and process
    - **content**: Raw markdown content to process
    - **file_path**: Path to a markdown file to process (alternative to content)
    
    Returns processed markdown document
    """
    try:
        # Priority: uploaded file > file_path > content
        if file:
            processed_content = await service.process_uploaded_file(file)
        elif file_path:
            content = service.load_markdown_file(file_path)
            processed_content = service.process_markdown(content)
        elif content:
            processed_content = service.process_markdown(content)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either content, file_path, or file upload must be provided"
            )
        
        # Create response
        response = MarkdownParseResponse(
            document=processed_content
        )
        
        return response
        
    except MarkdownServiceError as e:
        logger.error(f"Markdown service error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing markdown: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@router.post("/file", response_model=MarkdownParseResponse)
async def parse_markdown_file(
    file_path: str,
    service: MarkdownService = Depends(get_markdown_service)
):
    """
    Parse markdown from a file path
    
    - **file_path**: Path to the markdown file to process
    
    Returns processed markdown document
    """
    try:
        # Load content from file
        content = service.load_markdown_file(file_path)
        
        # Process the markdown
        processed_content = service.process_markdown(content)
        
        # Create response
        response = MarkdownParseResponse(
            document=processed_content
        )
        
        return response
        
    except MarkdownServiceError as e:
        logger.error(f"Markdown service error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing markdown file: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        ) 