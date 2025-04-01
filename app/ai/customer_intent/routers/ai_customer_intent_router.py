from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Request
from app.ai.customer_intent.models.ai_customer_intent_model import CustomerIntentResponse
from app.input_processing.core.services.file_handler_routing_logic_core_services import FileHandlerRoutingService, FileHandlerRoutingError
from app.input_processing.markdown.services.markdown_service import MarkdownService
from app.input_processing.docx.services.docx_service import DocxService
from app.input_processing.txt.services.txt_service import TxtService
from app.input_processing.core.services.input_processing_core_service import InputProcessingService, InputProcessingError
from app.ai.core.services.tokenizer_core_service import TokenizerService, TokenizerError
from app.ai.customer_intent.services.ai_customer_intent_service import CustomerIntentService
from app.ai.core.services.ai_core_service import AIService, OpenAIServiceError
from app.config.settings import OpenAISettings
from app.shared.logging import get_logger
import traceback
from typing import Dict, Any

# Set up module logger
logger = get_logger("customer_intent_router")

router = APIRouter(
    prefix="/customer-intent",
    tags=["customer-intent"],
)

# Initialize settings first
openai_settings = OpenAISettings()

# Create service instances with dependencies
file_handler_routing_service = FileHandlerRoutingService()
markdown_service = MarkdownService() 
docx_service = DocxService()
txt_service = TxtService()
tokenizer_service = TokenizerService(openai_settings)
ai_service = AIService(openai_settings)
customer_intent_service = CustomerIntentService()

# Custom exception for router-specific errors
class CustomerIntentRouterError(Exception):
    """Custom exception for customer intent router errors"""
    pass

# Helper functions for modular processing
async def extract_file_content(file: UploadFile, req_logger = logger) -> str:
    """
    Extract text from file content based on file type
    
    Args:
        file: Uploaded file
        req_logger: Logger to use for this request
        
    Returns:
        Extracted text from file
        
    Raises:
        CustomerIntentRouterError: If file processing fails
    """
    try:
        # 1. Determine file type based on extension
        file_type = file_handler_routing_service.validate_file_type(file)
        
        # 2. Read file contents
        file_content = await file.read()
        req_logger.debug(f"Read {len(file_content)} bytes from file")
        
        # 3. Extract text based on file type
        if file_type == "markdown":
            return markdown_service.extract_text(file_content)
        elif file_type == "docx":
            return docx_service.extract_text(file_content)
        elif file_type == "text":
            return txt_service.extract_text(file_content)
        else:
            raise CustomerIntentRouterError(f"Unsupported file type: {file_type}")
            
    except FileHandlerRoutingError as e:
        req_logger.error(f"File handler routing error: {str(e)}")
        raise CustomerIntentRouterError(f"Invalid file type: {str(e)}")
    except Exception as e:
        req_logger.error(f"Error processing file: {str(e)}")
        req_logger.error(f"Error type: {type(e)}")
        req_logger.error(f"Error traceback: {traceback.format_exc()}")
        raise CustomerIntentRouterError(f"Error processing file: {str(e)}")

def process_text(text: str, req_logger = logger) -> str:
    """
    Process document text to ensure it's clean and ready for the LLM
    
    Args:
        text: Raw document text from file upload
        req_logger: Logger to use for this request
        
    Returns:
        Processed text
        
    Raises:
        CustomerIntentRouterError: If text processing fails
    """
    try:
        # Validate the text
        assert text, "Document text cannot be empty"
        
        # Process the text using static method
        req_logger.debug("Processing document text from file")
        processed_text = InputProcessingService.process_text(text)
        
        # Validate the result
        assert processed_text, "Processed text cannot be empty"
        
        return processed_text
    except InputProcessingError as e:
        raise CustomerIntentRouterError(f"Error processing text: {str(e)}")
    except AssertionError as e:
        raise CustomerIntentRouterError(str(e))
    except Exception as e:
        raise CustomerIntentRouterError(f"Error processing text: {str(e)}")

def validate_token_count(processed_text: str, req_logger = logger) -> Dict[str, Any]:
    """
    Validate text against token limits
    
    Args:
        processed_text: Processed document text
        req_logger: Logger to use for this request
        
    Returns:
        Dictionary with token information
        
    Raises:
        CustomerIntentRouterError: If token validation fails
    """
    try:
        # Log input details
        req_logger.debug(f"Validating tokens for text length: {len(processed_text)}")
        req_logger.debug(f"First 100 chars of text: {processed_text[:100]}...")
        
        # Log model configuration
        req_logger.debug(f"Current model: {openai_settings.default_model}")
        print(f"Current model: {openai_settings.default_model}")
        req_logger.debug(f"Model encoding: {openai_settings.encoding}")
        
        # Validate tokens using tokenizer service
        req_logger.debug("Calling tokenizer service validate_tokens")
        token_info = tokenizer_service.validate_tokens(processed_text)
        
        # Log token counts and model info
        req_logger.info(f"Token count: {token_info['token_count']}/{token_info['model_limit']} ({token_info['percentage_used']}%)")
        req_logger.info(f"Using model: {token_info['model']} ({token_info['model_family']})")
        req_logger.debug(f"Model capabilities: {token_info['capabilities']}")
        req_logger.debug(f"Full token info: {token_info}")
        
        # Return token information
        return token_info
        
    except TokenizerError as e:
        req_logger.error(f"Tokenizer error: {str(e)}")
        req_logger.error(f"Error type: {type(e)}")
        req_logger.error(f"Error traceback: {traceback.format_exc()}")
        raise CustomerIntentRouterError(f"Tokenizer error: {str(e)}")
    except Exception as e:
        req_logger.error(f"Unexpected error in token validation: {str(e)}")
        req_logger.error(f"Error type: {type(e)}")
        req_logger.error(f"Error traceback: {traceback.format_exc()}")
        if isinstance(e, CustomerIntentRouterError):
            raise
        raise CustomerIntentRouterError(f"Error validating token count: {str(e)}")

async def generate_intent(processed_text: str, req_logger = logger) -> Dict[str, Any]:
    """
    Generate customer intent using AI service
    
    Args:
        processed_text: Processed document text
        req_logger: Logger to use for this request
        
    Returns:
        Dictionary with intent result
        
    Raises:
        CustomerIntentRouterError: If intent generation fails
    """
    try:
        # Validate inputs
        assert processed_text, "Text cannot be empty for intent generation"
        
        # Generate the prompt
        req_logger.info("Generating customer intent prompt")
        messages = customer_intent_service.format_customer_intent_prompt(processed_text)
        
        # Call AI service directly
        req_logger.info("Calling AI service")
        completion = await ai_service.generate_completion(messages=messages["messages"])
        
        # Validate the result
        assert "text" in completion, "Text missing from completion"
        assert "model" in completion, "Model missing from completion"
        assert "usage" in completion, "Usage missing from completion"
        
        # Log completion stats
        req_logger.info(f"Intent generated using model: {completion['model']}")
        req_logger.debug(f"Usage stats: {completion['usage']}")
        
        # Format the result
        return {
            "intent": completion["text"].strip(),
            "model": completion["model"],
            "usage": completion["usage"]
        }
        
    except OpenAIServiceError as e:
        raise CustomerIntentRouterError(f"AI service error: {str(e)}")
    except ValueError as e:
        raise CustomerIntentRouterError(f"Invalid input: {str(e)}")
    except AssertionError as e:
        raise CustomerIntentRouterError(str(e))
    except Exception as e:
        if isinstance(e, CustomerIntentRouterError):
            raise
        raise CustomerIntentRouterError(f"Error generating intent: {str(e)}")

def format_response(intent_result: Dict[str, Any], token_info: Dict[str, Any], processed_text: str, req_logger = logger) -> CustomerIntentResponse:
    """
    Format the final response
    
    Args:
        intent_result: Intent generation result
        token_info: Token information
        processed_text: The processed text that was used to generate the intent
        req_logger: Logger to use for this request
        
    Returns:
        Formatted CustomerIntentResponse
    """
    try:
        # Validate inputs
        assert intent_result is not None, "Intent result cannot be None"
        assert token_info is not None, "Token info cannot be None"
        assert processed_text is not None, "Processed text cannot be None"
        assert "intent" in intent_result, "Intent must be in result"
        assert "model" in intent_result, "Model must be in result"
        assert "usage" in intent_result, "Usage must be in result"
        assert "model_limit" in token_info, "Model limit must be in token info"
        assert "token_count" in token_info, "Token count must be in token info"
        assert "tokens_remaining" in token_info, "Remaining tokens must be in token info"
        assert "model_family" in token_info, "Model family must be in token info"
        assert "capabilities" in token_info, "Capabilities must be in token info"
        
        # Create response
        req_logger.debug("Formatting response")
        return CustomerIntentResponse(
            intent=intent_result["intent"],
            model=intent_result["model"],
            model_family=token_info["model_family"],
            capabilities=token_info["capabilities"],
            usage=intent_result["usage"],
            token_limit=token_info["model_limit"],
            token_count=token_info["token_count"],
            remaining_tokens=token_info["tokens_remaining"],
            text_used=processed_text
        )
    except AssertionError as e:
        raise CustomerIntentRouterError(f"Error formatting response: {str(e)}")
    except Exception as e:
        raise CustomerIntentRouterError(f"Error formatting response: {str(e)}")

@router.post("", response_model=CustomerIntentResponse)
async def generate_customer_intent(
    request: Request,
    file: UploadFile = File(...)
):
    """
    Generate a customer intent statement based on an uploaded document.
    
    This endpoint processes an uploaded document and formats a customer intent statement in the form:
    "As a [user type], I want to [action] because [reason]"
    
    Parameters:
    - **file**: The document file to upload (.md, .docx, .txt)
    
    Returns a customer intent statement derived from the document.
    """
    # Get request-specific logger or use module logger as fallback
    req_logger = getattr(request.state, "logger", logger)
    
    try:
        # Log request start
        req_logger.info("Processing customer intent request")
        
        # 1. Process file content
        document_text = await extract_file_content(file, req_logger)
        
        # 2. Process text for LLM
        processed_text = process_text(document_text, req_logger)
        
        # 3. Validate token count
        token_info = validate_token_count(processed_text, req_logger)
        
        # 4. Generate customer intent
        intent_result = await generate_intent(processed_text, req_logger)
        
        # 5. Format and return response
        response = format_response(intent_result, token_info, processed_text, req_logger)
        req_logger.info("Customer intent generation completed successfully")
        return response
        
    except CustomerIntentRouterError as e:
        # Handle router-specific errors
        req_logger.error(f"Customer intent router error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except OpenAIServiceError as e:
        # Handle OpenAI service errors
        req_logger.error(f"OpenAI service error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error calling AI service: {str(e)}"
        )
    except Exception as e:
        # Handle unexpected errors
        req_logger.error(f"Unexpected error in customer intent generation: {str(e)}")
        req_logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while generating the customer intent"
        ) 