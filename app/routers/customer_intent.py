from fastapi import APIRouter, Depends, HTTPException, status
from app.models.customer_intent_models import CustomerIntentRequest, CustomerIntentResponse
from app.services.customer_intent_service import CustomerIntentService
from app.services.openai_service import OpenAIService, OpenAIServiceError
import logging

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/customer-intent",
    tags=["customer-intent"],
)

# Create service instance
openai_service = OpenAIService()
customer_intent_service = CustomerIntentService(openai_service)

@router.post("/generate", response_model=CustomerIntentResponse)
async def generate_customer_intent(request: CustomerIntentRequest):
    """
    Generate a customer intent statement based on document text.
    
    This endpoint takes document text and formats a customer intent statement in the form:
    "As a [user type], I want to [action] because [reason]"
    
    - **document_text**: The document text to use as basis for the intent
    - **user_type**: Optional specific user type to focus on
    - **max_tokens**: Maximum tokens to generate (default: 150)
    - **temperature**: Temperature for generation (0.0-1.0, default: 0.5)
    
    Returns a customer intent statement derived from the document.
    """
    try:
        # Call the service
        result = await customer_intent_service.generate_customer_intent(
            document_text=request.document_text,
            user_type=request.user_type,
            max_tokens=request.max_tokens or 150,
            temperature=request.temperature or 0.5
        )
        
        # Return the response
        return CustomerIntentResponse(
            intent=result["intent"],
            model=result["model"],
            usage=result["usage"]
        )
    except OpenAIServiceError as e:
        # Log the error and return an appropriate status code
        logger.error(f"OpenAI service error in customer intent generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error generating customer intent: {str(e)}"
        )
    except Exception as e:
        # Log unexpected errors but don't expose details to client
        logger.error(f"Unexpected error in customer intent generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while generating the customer intent."
        ) 