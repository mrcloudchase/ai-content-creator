# Content Generate Feature - Implementation Plan

## 1. Overview

This plan outlines the implementation of a new `/api/v1/content-generate` endpoint that will create content for selected content types using customer intent and processed text. This endpoint will form the third part of the content creation workflow:

1. Customer intent generation (`/api/v1/customer-intent`) - Extracts text from documents and creates structured user stories
2. Content type selection (`/api/v1/content-types`) - Determines appropriate content types based on intent and text
3. Content generation (`/api/v1/content-generate`) - Creates actual content using the content types, intent, and text

## 2. Feature Requirements

### 2.1 Functional Requirements

- Accept customer intent, processed text, and selected content types as input
- Generate content for each selected content type using the templates defined in `content_types_config.py`
- Return the generated content along with metadata about the processing
- Handle appropriate validation and error conditions
- Follow the established architectural patterns of the existing application

### 2.2 Non-Functional Requirements

- Response time under 10 seconds (may take longer than other endpoints due to the size of the generated content)
- Token management to ensure content can be generated within model limits
- Follow existing coding standards and module structure
- Include proper error handling, logging, and testing

## 3. Implementation Plan

### 3.1 Model Definitions

1. Create `app/ai/content_generate/models/content_generate_model.py`:

```python
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ContentTypeRequest(BaseModel):
    """Model representing a single content type request"""
    type: str = Field(..., description="The content type (tutorial, how-to, explanation, reference)")
    title: Optional[str] = Field(None, description="Optional title for the content")

class ContentGenerateRequest(BaseModel):
    """Request model for content generation"""
    intent: str = Field(..., description="The customer intent statement")
    text_used: str = Field(..., description="The source text to analyze")
    content_types: List[ContentTypeRequest] = Field(..., description="List of content types to generate")

class GeneratedContent(BaseModel):
    """Model representing a single piece of generated content"""
    type: str = Field(..., description="The content type (tutorial, how-to, explanation, reference)")
    title: str = Field(..., description="The title of the generated content")
    content: str = Field(..., description="The generated content in markdown format")

class ContentGenerateResponse(BaseModel):
    """Response model for content generation"""
    generated_content: List[GeneratedContent] = Field(..., description="List of generated content items")
    model: str = Field(..., description="Model used for generation")
    model_family: str = Field(..., description="Family of the model used")
    capabilities: Dict[str, Any] = Field(..., description="Capabilities of the model used")
    usage: Dict[str, int] = Field(..., description="Token usage statistics")
    token_limit: int = Field(..., description="Maximum allowed tokens")
    token_count: int = Field(..., description="Number of tokens used")
    remaining_tokens: int = Field(..., description="Remaining tokens available")
    text_used: str = Field(..., description="The text used for generation")
```

### 3.2 Service Implementation

1. Create `app/ai/content_generate/services/content_generate_service.py`:

```python
from typing import Dict, Any, List
from app.ai.content_types.models.content_types_config import CONTENT_TYPES

class ContentGenerateService:
    """Service for content generation operations"""
    
    def format_content_generate_prompt(self, 
                                      content_type: str, 
                                      intent: str, 
                                      text: str,
                                      title: str = None) -> Dict[str, Any]:
        """
        Format the prompt for content generation for a specific content type
        
        Args:
            content_type: The content type to generate (tutorial, how-to, explanation, reference)
            intent: The customer intent statement
            text: The source text to use
            title: Optional title for the content
            
        Returns:
            Formatted prompt for the LLM
        """
        # Input validation
        if content_type not in CONTENT_TYPES:
            raise ValueError(f"Invalid content type: {content_type}")
        if not intent or not intent.strip():
            raise ValueError("Intent cannot be empty")
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        # Get content type details
        type_info = CONTENT_TYPES[content_type]
        type_name = type_info["name"]
        type_description = type_info["description"]
        type_purpose = type_info["purpose"]
        type_template = type_info["markdown_template"]
        
        # Create a system prompt that explains the task
        system_prompt = f"""
        You are an AI content creation assistant specialized in creating {type_name} content.
        
        About this content type:
        - Name: {type_name}
        - Description: {type_description}
        - Purpose: {type_purpose}
        
        Your task is to create {type_name} content based on:
        1. The customer intent statement
        2. The provided source text
        3. The markdown template structure shown below
        
        Template structure:
        ```markdown
        {type_template}
        ```
        
        Guidelines:
        - Create high-quality, comprehensive content that fulfills the purpose of a {type_name}
        - Use the provided template structure, but adapt section headers as needed
        - Fill in all placeholder content with relevant, detailed information
        - Use information from the source text where applicable
        - Keep the tone professional and informative
        - Use proper markdown formatting including code blocks, lists, and tables as appropriate
        - If a title is provided, use it; otherwise, create an appropriate title
        - Generate content that completely fulfills the customer intent
        
        Return only the final markdown content with no additional text.
        """
        
        # Create a user prompt with the intent, text and title
        title_text = f"Title: {title}" if title else "Please create an appropriate title"
        user_prompt = f"""
        Customer Intent: {intent}
        
        {title_text}
        
        Source Text:
        {text}
        
        Please generate {type_name} content following the template structure.
        """
        
        # Return the formatted messages
        return {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        }
```

### 3.3 Router Implementation

1. Create `app/ai/content_generate/routers/content_generate_router.py`:

```python
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
            messages=prompt["messages"],
            temperature=0.7  # Higher temperature for creative content generation
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
```

### 3.4 Update the Main Application

1. Update `app/main.py` to include the new router:

```python
# Add import
from app.ai.content_generate.routers.content_generate_router import router as content_generate_router

# Include the Content Generate router with proper prefix
app.include_router(
    content_generate_router,
    prefix=API_V1_PREFIX
)

# Update root endpoint to include the new endpoint
@app.get("/")
async def root(request: Request):
    # ...existing code...
    
    return {
        # ...existing keys...
        "endpoints": {
            # ...existing endpoints...
            "content_generate": f"{API_V1_PREFIX}/content-generate - Generate content based on intent, text, and content types"
        }
    }
```

## 4. Testing Plan

### 4.1 Unit Tests

1. Create `tests/unit/ai/content_generate/services/test_content_generate_service.py`:
   - Test prompt formatting for each content type
   - Test error handling for invalid inputs
   - Test template substitution

2. Create `tests/unit/ai/content_generate/routers/test_content_generate_router.py`:
   - Test token validation logic
   - Test content generation for single type
   - Test content generation for multiple types
   - Test response formatting
   - Test error handling

### 4.2 Integration Tests

1. Create `tests/integration/test_content_generate_endpoint.py`:
   - Test the full workflow from request to response
   - Test with different content types
   - Test error handling
   - Test with mocked AI responses

### 4.3 End-to-End Tests

1. Create a full workflow test that connects all three endpoints:
   - Upload document → Extract text → Generate intent
   - Use intent and text → Select content types
   - Use intent, text, and content types → Generate content

## 5. Implementation Timeline

1. **Phase 1: Core Implementation** (1-2 days)
   - Implement models
   - Implement service layer
   - Implement router logic
   - Update main application

2. **Phase 2: Testing** (1-2 days)
   - Write unit tests
   - Write integration tests
   - Write end-to-end tests

3. **Phase 3: Documentation & Polish** (1 day)
   - Update API documentation
   - Add examples to README
   - Review and optimize token usage

## 6. Future Enhancements

1. Add support for content templates customization
2. Implement content generation metadata (target audience, complexity level)
3. Add support for generating multiple formats (markdown, HTML, etc.)
4. Add support for image generation prompts within content
5. Implement caching for common content generation patterns
6. Add content quality scoring metrics

## 7. Conclusion

This plan outlines a comprehensive approach to implementing the content generation endpoint that follows the existing patterns and architectural decisions of the application. The implementation reuses much of the existing functionality while providing a new crucial feature to complete the content creation workflow.

Once implemented, users will be able to go from raw documents to fully structured, high-quality content using the three-step API workflow, with each step building on the outputs of the previous steps. 