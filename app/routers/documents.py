from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from fastapi.responses import PlainTextResponse, JSONResponse
from app.services.docx_parser import DocxParser, DocxParserError, TokenLimitError
import traceback
import logging
import json

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
)

async def validate_docx_file(file: UploadFile = File(...)):
    """
    Dependency that validates the uploaded file is a valid .docx file
    
    Args:
        file: The uploaded file
        
    Returns:
        The file if validation passes
        
    Raises:
        HTTPException: If validation fails
    """
    # Check if file exists
    if file is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided."
        )
    
    # Check if filename is present
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is missing."
        )
    
    # Check file extension
    if not file.filename.endswith('.docx'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only .docx files are supported."
        )
    
    # Check content type (though this can be spoofed)
    content_type = file.content_type
    if content_type != "application/vnd.openxmlformats-officedocument.wordprocessingml.document" and \
       "officedocument.wordprocessingml.document" not in content_type:
        logger.warning(f"Suspicious content type: {content_type} for file {file.filename}")
    
    return file

@router.post("/extract-text")
async def extract_document_text(file: UploadFile = Depends(validate_docx_file)):
    """
    Extract text content from a .docx document and return as a structured JSON response
    
    - **file**: .docx file to parse
    
    Returns a JSON object with the parsed document text in the "document" field
    
    The output is thoroughly sanitized to be JSON-compatible and can be used directly 
    with the AI completion endpoint without any additional processing. All control 
    characters, quotes, and special characters are properly escaped for use in nested 
    JSON contexts.
    
    Example usage with AI endpoint:
    ```
    # 1. Extract text from document
    response = requests.post("/api/v1/documents/extract-text", files={"file": file})
    parsed_data = response.json()
    
    # 2. Use the document text directly in AI request
    ai_response = requests.post("/api/v1/ai/completions", json={
        "prompt": parsed_data["document"],
        "max_tokens": 500
    })
    ```
    
    Token counting is performed to ensure the document is not too large for the 
    configured OpenAI model.
    """
    try:
        # Read file content with proper error handling
        try:
            content = await file.read()
        except Exception as e:
            logger.error(f"Error reading file: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Error reading the uploaded file."
            )
        
        # Check if content is empty
        if not content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty file was provided."
            )
            
        # Check file size (arbitrary limit of 20MB for example)
        if len(content) > 20 * 1024 * 1024:  # 20MB
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File too large. Maximum file size is 20MB."
            )
            
        # Extract the text from the document
        try:
            document_text = DocxParser.extract_text(content)
            
            # Additional JSON validation to ensure the response can be used in nested contexts
            try:
                # Test that the text works in a nested JSON context (copy-paste scenario)
                nested_test = json.dumps({"outer": json.dumps({"prompt": document_text})})
                json.loads(nested_test)  # Should parse without errors
            except json.JSONDecodeError as e:
                logger.error(f"JSON compatibility validation failed: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Document text failed JSON compatibility validation. Please report this error."
                )
                
        except TokenLimitError as e:
            # Return a specific error for token limit issues
            logger.warning(f"Token limit exceeded: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content={
                    "detail": str(e),
                    "error_type": "token_limit_exceeded"
                }
            )
        except AssertionError as e:
            # Handle assertion errors from our validation
            logger.error(f"Validation error in parser: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Document validation error: {str(e)}"
            )
        except DocxParserError as e:
            logger.error(f"Error parsing document: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Error parsing document: {str(e)}"
            )
        
        # Return the text content in a "document" field
        return {"document": document_text}
        
    except HTTPException:
        # Re-raise HTTP exceptions as they already have the right format
        raise
    except Exception as e:
        # Log the error for debugging but don't expose details to the client
        logger.error(f"Unexpected error: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing the document."
        ) 