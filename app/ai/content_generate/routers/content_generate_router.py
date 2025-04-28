from fastapi import APIRouter, HTTPException, Request
from app.ai.content_generate.models.content_generate_model import ContentGenerateRequest, ContentGenerateResponse, GeneratedContent
from app.ai.content_generate.services.content_generate_service import ContentGenerateService
from app.ai.core.services.ai_core_service import AIService, OpenAIServiceError
from app.ai.core.services.tokenizer_core_service import TokenizerService, TokenizerError
from app.config.settings import OpenAISettings
from app.shared.logging import get_logger
import traceback
from typing import Dict, Any, List

# Set up module logger
logger = get_logger("content_generate_router")

router = APIRouter(
    prefix="/content-generate",
    tags=["content-generate"],
)

# Initialize settings first
openai_settings = OpenAISettings()

# Create service instances with dependencies
tokenizer_service = TokenizerService(openai_settings)
ai_service = AIService(openai_settings)
content_generate_service = ContentGenerateService()

# Custom exception for router-specific errors
class ContentGenerateRouterError(Exception):
    """Custom exception for content generation router errors"""
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
        ContentGenerateRouterError: If token validation fails
    """
    try:
        # Log input details
        req_logger.debug(f"Validating tokens for text length: {len(text)}")
        
        # Validate tokens using tokenizer service
        token_info = tokenizer_service.validate_tokens(text)
        
        # Log token counts and model info
        req_logger.info(f"Token count: {token_info['token_count']}/{token_info['model_limit']} ({token_info['percentage_used']}%)")
        
        # Return token information
        return token_info
        
    except TokenizerError as e:
        req_logger.error(f"Tokenizer error: {str(e)}")
        raise ContentGenerateRouterError(f"Tokenizer error: {str(e)}")
    except Exception as e:
        req_logger.error(f"Unexpected error in token validation: {str(e)}")
        if isinstance(e, ContentGenerateRouterError):
            raise
        raise ContentGenerateRouterError(f"Error validating token count: {str(e)}")

async def generate_content_for_type(
    content_type: str,
    title: str,
    intent: str,
    text: str,
    req_logger = logger
) -> str:
    """
    Generate content for a specific content type
    
    Args:
        content_type: Content type to generate
        title: Optional title for the content
        intent: Customer intent statement
        text: Source text
        req_logger: Logger to use for this request
        
    Returns:
        Generated content in markdown format
        
    Raises:
        ContentGenerateRouterError: If content generation fails
    """
    try:
        # Format the prompt
        req_logger.info(f"Generating content for type: {content_type}")
        prompt = content_generate_service.format_content_generate_prompt(
            content_type=content_type,
            intent=intent,
            text=text,
            title=title
        )
        
        # Generate completion
        req_logger.info("Calling AI service")
        completion = await ai_service.generate_completion(
            messages=prompt["messages"]
        )
        
        # Extract content
        generated_content = completion.get('text', '')
        
        if not generated_content:
            raise ContentGenerateRouterError("Empty response from LLM")
            
        req_logger.info(f"Generated {len(generated_content)} characters of content")
        return generated_content
            
    except OpenAIServiceError as e:
        req_logger.error(f"AI service error: {str(e)}")
        raise ContentGenerateRouterError(f"AI service error: {str(e)}")
    except Exception as e:
        req_logger.error(f"Error generating content: {str(e)}")
        if isinstance(e, ContentGenerateRouterError):
            raise
        raise ContentGenerateRouterError(f"Error generating content: {str(e)}")

async def generate_all_content(
    request: ContentGenerateRequest,
    token_info: Dict[str, Any],
    req_logger = logger
) -> List[GeneratedContent]:
    """
    Generate content for all requested content types
    
    Args:
        request: The content generation request
        token_info: Token information
        req_logger: Logger to use for this request
        
    Returns:
        List of generated content items
        
    Raises:
        ContentGenerateRouterError: If content generation fails
    """
    # Initialize result list
    generated_content_list = []
    
    # Process each content type
    for content_type_request in request.content_types:
        try:
            # Generate content for this type
            content = await generate_content_for_type(
                content_type=content_type_request.type,
                title=content_type_request.title,
                intent=request.intent,
                text=request.text_used,
                req_logger=req_logger
            )
            
            # Extract title from content (first h1 header)
            title_lines = [line.replace('# ', '') for line in content.split('\n') if line.startswith('# ')]
            title = content_type_request.title or (title_lines[0] if title_lines else "Untitled")
            
            # Add to result list
            generated_content_list.append(
                GeneratedContent(
                    type=content_type_request.type,
                    title=title,
                    content=content
                )
            )
            
        except Exception as e:
            req_logger.error(f"Error generating content for type {content_type_request.type}: {str(e)}")
            req_logger.error(f"Continuing with other content types")
            # Continue with other content types even if one fails
    
    # Verify we have at least one successful generation
    if not generated_content_list:
        raise ContentGenerateRouterError("Failed to generate content for all requested types")
        
    return generated_content_list

def format_response(
    generated_content: List[GeneratedContent],
    token_info: Dict[str, Any],
    text_used: str,
    req_logger = logger
) -> ContentGenerateResponse:
    """
    Format the response for the content generation endpoint
    
    Args:
        generated_content: List of generated content items
        token_info: Token information
        text_used: The text used for generation
        req_logger: Logger to use for this request
        
    Returns:
        Formatted response
        
    Raises:
        ContentGenerateRouterError: If response formatting fails
    """
    try:
        # Format response
        response = ContentGenerateResponse(
            generated_content=generated_content,
            model=token_info.get("model", "unknown"),
            model_family=token_info.get("model_family", "unknown"),
            capabilities=token_info.get("capabilities", {}),
            usage=token_info.get("usage", {}), 
            token_limit=token_info.get("model_limit", 0),
            token_count=token_info.get("token_count", 0),
            remaining_tokens=token_info.get("tokens_remaining", 0),
            text_used=text_used
        )
        
        req_logger.debug("Response formatted successfully")
        return response
    except Exception as e:
        req_logger.error(f"Error formatting response: {str(e)}")
        raise ContentGenerateRouterError(f"Error formatting response: {str(e)}")

@router.post("", response_model=ContentGenerateResponse)
async def generate_content_endpoint(
    request: Request,
    content_request: ContentGenerateRequest
) -> ContentGenerateResponse:
    """
    Generate content based on customer intent, source text, and selected content types.
    
    This endpoint creates detailed markdown content for each requested content type,
    using the content type templates and the provided intent and source text.
    
    Parameters:
    - **intent**: The customer intent statement (As a [user], I want to [action] because [reason])
    - **text_used**: The source text to use as the basis for content
    - **content_types**: List of content types to generate, with optional titles
    
    Returns content for each requested type, along with metadata.
    """
    # Get request-specific logger or use module logger as fallback
    req_logger = getattr(request.state, "logger", logger)
    
    try:
        # Log request start
        req_logger.info("Processing content generation request")
        
        # 1. Validate token count
        token_info = validate_token_count(content_request.text_used, req_logger)
        
        # 2. Generate content for all requested types
        generated_content = await generate_all_content(
            request=content_request,
            token_info=token_info,
            req_logger=req_logger
        )
        
        # 3. Format and return response
        response = format_response(
            generated_content=generated_content,
            token_info=token_info,
            text_used=content_request.text_used,
            req_logger=req_logger
        )
        
        req_logger.info("Content generation completed successfully")
        return response
        
    except ContentGenerateRouterError as e:
        # Handle router-specific errors
        req_logger.error(f"Content generation router error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except OpenAIServiceError as e:
        # Handle OpenAI service errors
        req_logger.error(f"OpenAI service error: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Error calling AI service: {str(e)}"
        )
    except Exception as e:
        # Handle unexpected errors
        req_logger.error(f"Unexpected error in content generation: {str(e)}")
        req_logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while generating content"
        ) 