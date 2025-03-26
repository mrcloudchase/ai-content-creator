from fastapi import APIRouter, HTTPException, Depends, status
from app.models.ai_models import AIPromptRequest, AIResponse, AIUsage
from app.services.openai_service import OpenAIService, OpenAIServiceError
from app.config.settings import OpenAISettings
import logging

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/ai",
    tags=["ai"],
)

async def get_openai_service():
    """Dependency to get OpenAI service instance"""
    try:
        settings = OpenAISettings()
        return OpenAIService(settings)
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI service: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service is currently unavailable"
        )

@router.post("/completions", response_model=AIResponse)
async def generate_completion(
    request: AIPromptRequest,
    service: OpenAIService = Depends(get_openai_service)
):
    """
    Generate a completion from OpenAI based on the provided prompt
    
    - **prompt**: The text prompt to send to OpenAI
    - **model**: Optional model to use (defaults to configured model)
    - **max_tokens**: Optional maximum tokens to generate
    - **temperature**: Optional temperature for generation
    
    Returns the generated text response and usage statistics
    """
    # Input validation - check this before making API calls
    if not request.prompt or not request.prompt.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Prompt cannot be empty"
        )
            
    try:
        # Call OpenAI service
        result = await service.generate_completion(
            prompt=request.prompt,
            model=request.model,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        # Create response model from result
        response = AIResponse(
            text=result["text"],
            model=result["model"],
            usage=AIUsage(
                prompt_tokens=result["usage"]["prompt_tokens"],
                completion_tokens=result["usage"]["completion_tokens"],
                total_tokens=result["usage"]["total_tokens"]
            )
        )
        
        return response
        
    except OpenAIServiceError as e:
        logger.error(f"OpenAI service error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error calling OpenAI: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        ) 