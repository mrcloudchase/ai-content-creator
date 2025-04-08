from fastapi import APIRouter, HTTPException, Depends
from app.ai.content_types.models.content_type_model import ContentTypeRequest, ContentTypeResponse, ContentTypeSelection
from app.ai.content_types.models.content_types_config import CONTENT_TYPES
from app.ai.content_types.services.content_type_service import ContentTypeService
from app.ai.core.services.ai_core_service import AIService
from app.ai.core.services.tokenizer_core_service import TokenizerService, TokenizerError
from app.config.settings import OpenAISettings
from app.shared.logging import get_logger
import json
import traceback
from typing import Dict, Any, List

# Set up module logger
logger = get_logger("content_type_router")

# Define content types based on the Diátaxis framework
# Moved to app/ai/content_types/models/content_types_config.py

router = APIRouter(
    prefix="/content-types",
    tags=["content-types"],
)

# Initialize settings first
openai_settings = OpenAISettings()

# Create service instances with dependencies
tokenizer_service = TokenizerService(openai_settings)
ai_service = AIService(openai_settings)
content_type_service = ContentTypeService()

# Custom exception for router-specific errors
class ContentTypeRouterError(Exception):
    """Custom exception for content type router errors"""
    pass

def validate_token_count(text: str, req_logger = logger) -> Dict[str, Any]:
    """
    Validate text against token limits
    
    Args:
        text: Text to validate
        req_logger: Logger to use for this request
        
    Returns:
        Dictionary with token information
        
    Raises:
        ContentTypeRouterError: If token validation fails
    """
    try:
        # Log input details
        req_logger.debug(f"Validating tokens for text length: {len(text)}")
        
        # Log model configuration
        req_logger.debug(f"Current model: {openai_settings.default_model}")
        req_logger.debug(f"Model encoding: {openai_settings.encoding}")
        
        # Validate tokens using tokenizer service
        req_logger.debug("Calling tokenizer service validate_tokens")
        token_info = tokenizer_service.validate_tokens(text)
        
        # Log token counts and model info
        req_logger.info(f"Token count: {token_info['token_count']}/{token_info['model_limit']} ({token_info['percentage_used']}%)")
        req_logger.info(f"Using model: {token_info['model']} ({token_info['model_family']})")
        req_logger.debug(f"Model capabilities: {token_info['capabilities']}")
        
        # Return token information
        return token_info
        
    except TokenizerError as e:
        req_logger.error(f"Tokenizer error: {str(e)}")
        req_logger.error(f"Error type: {type(e)}")
        req_logger.error(f"Error traceback: {traceback.format_exc()}")
        raise ContentTypeRouterError(f"Tokenizer error: {str(e)}")
    except Exception as e:
        req_logger.error(f"Unexpected error in token validation: {str(e)}")
        req_logger.error(f"Error type: {type(e)}")
        req_logger.error(f"Error traceback: {traceback.format_exc()}")
        if isinstance(e, ContentTypeRouterError):
            raise
        raise ContentTypeRouterError(f"Error validating token count: {str(e)}")

async def select_content_types(
    intent: str,
    text_used: str,
    ai_service: AIService,
    token_service: TokenizerService,
    token_info: Dict[str, Any],
    logger: Any
) -> ContentTypeResponse:
    """Select content types based on customer intent and source text."""
    try:
        # Format the prompt
        prompt = content_type_service.format_content_type_prompt(intent, text_used)
        
        # Generate completion - use same format as customer intent router
        completion = await ai_service.generate_completion(messages=prompt["messages"])
        
        # Log the response
        logger.info(f"Response usage: {completion.get('usage', {})}")
        
        # Extract the content from the response - handle the format returned by AIService
        content = completion.get('text', '')
        
        if not content:
            raise ContentTypeRouterError("Empty response from LLM")
            
        # Parse the response
        try:
            # The response should be a JSON string
            content_data = json.loads(content)
            
            # Validate the response structure
            if not isinstance(content_data, dict):
                raise ContentTypeRouterError("Invalid response format: expected a dictionary")
                
            if 'content_types' not in content_data:
                raise ContentTypeRouterError("Invalid response format: missing 'content_types' key")
                
            # Transform content_types to selected_types format
            selected_types = []
            for content_type in content_data['content_types']:
                selected_types.append(ContentTypeSelection(
                    type=content_type.get('type', ''),
                    confidence=content_type.get('confidence', 0),
                    reasoning=content_type.get('reasoning', '')
                ))
                
            # Create the response
            return ContentTypeResponse(
                selected_types=selected_types,
                model=completion.get('model', 'unknown'),
                model_family=token_info.get("model_family", "unknown"),
                capabilities=token_info.get("capabilities", {}),
                usage=completion.get('usage', {}),
                token_limit=token_info.get("model_limit", 0),
                token_count=token_info.get("token_count", 0),
                remaining_tokens=token_info.get("tokens_remaining", 0),
                text_used=text_used
            )
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing LLM response: {str(e)}")
            logger.error(f"Raw response: {content}")
            raise ContentTypeRouterError(f"Error parsing LLM response: {str(e)}")
            
    except Exception as e:
        logger.error(f"Error selecting content types: {str(e)}")
        raise ContentTypeRouterError(f"Error selecting content types: {str(e)}")

def format_response(selected_types: List[ContentTypeSelection], token_info: Dict[str, Any], req_logger = logger) -> ContentTypeResponse:
    """
    Format the response for the content types endpoint
    
    Args:
        selected_types: List of selected content types
        token_info: Token information
        req_logger: Logger to use for this request
        
    Returns:
        Formatted response
        
    Raises:
        ContentTypeRouterError: If response formatting fails
    """
    try:
        # Format response
        response = ContentTypeResponse(
            selected_types=selected_types,
            model=token_info.get("model", "unknown"),
            model_family=token_info.get("model_family", "unknown"),
            capabilities=token_info.get("capabilities", {}),
            usage=token_info.get("usage", {}),
            token_limit=token_info.get("model_limit", 0),
            token_count=token_info.get("token_count", 0),
            remaining_tokens=token_info.get("tokens_remaining", 0)
        )
        
        req_logger.debug(f"Response formatted: {response}")
        return response
    except Exception as e:
        req_logger.error(f"Error formatting response: {str(e)}")
        req_logger.error(f"Error type: {type(e)}")
        req_logger.error(f"Error traceback: {traceback.format_exc()}")
        raise ContentTypeRouterError(f"Error formatting response: {str(e)}")

@router.post("/content-types", response_model=ContentTypeResponse)
async def select_content_types_endpoint(
    request: ContentTypeRequest
) -> ContentTypeResponse:
    """
    Select appropriate content types based on customer intent and source text.
    
    Args:
        request: The request containing intent and source text
        
    Returns:
        ContentTypeResponse with selected content types and metadata
        
    Raises:
        HTTPException: If content type selection fails
    """
    try:
        # Extract request data
        intent = request.intent
        text = request.text_used
        
        # Validate token count
        token_info = validate_token_count(text, logger)
        
        # Select content types
        response = await select_content_types(
            intent=intent,
            text_used=text,
            ai_service=ai_service,
            token_service=tokenizer_service,
            token_info=token_info,
            logger=logger
        )
        
        return response
        
    except ContentTypeRouterError as e:
        logger.error(f"Content type error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Error selecting content types: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        ) 