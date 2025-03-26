from fastapi import APIRouter, HTTPException, status
from app.models.token_models import TokenCountRequest, TokenCountResponse
from app.services.token_service import TokenService, TokenServiceError
import logging

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/tokens",
    tags=["tokens"],
)

@router.post("/count", response_model=TokenCountResponse)
async def count_tokens(request: TokenCountRequest):
    """
    Count the number of tokens in a text string
    
    - **text**: The text to count tokens for
    - **model**: Optional model to use for token counting (defaults to gpt-3.5-turbo)
    
    Returns token count and context usage information
    """
    # Input validation
    if not request.text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text cannot be empty"
        )
            
    try:
        # Count tokens using the service
        result = TokenService.count_tokens(
            text=request.text,
            model_name=request.model
        )
        
        # Create and return the response
        return TokenCountResponse(**result)
        
    except TokenServiceError as e:
        logger.error(f"Token service error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error counting tokens: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        ) 