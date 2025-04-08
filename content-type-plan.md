# Content Types Endpoint Implementation Plan

## 1. Overview

The `/api/v1/content-types` endpoint will follow the same structure as the existing customer intent endpoint. It will use an LLM to analyze customer intent and source text to determine appropriate content types from the Diátaxis framework.

## 2. Architecture Components

### 2.1 New Components

1. **ContentTypeService** (`app/ai/content_types/services/content_type_service.py`)
   - Purpose: Format prompts for content type selection
   - Dependencies: None (similar to CustomerIntentService)
   - Key method: `format_content_type_prompt(intent: str, text: str) -> Dict[str, Any]`

2. **ContentTypeModel** (`app/ai/content_types/models/content_type_model.py`)
   - Purpose: Define request and response models
   - Dependencies: Pydantic
   - Key classes:
     - `ContentTypeSelection`
     - `ContentTypeRequest`
     - `ContentTypeResponse`

3. **ContentTypeRouter** (`app/ai/content_types/routers/content_type_router.py`)
   - Purpose: Handle HTTP requests and coordinate service calls
   - Dependencies: 
     - ContentTypeService
     - AIService
     - TokenizerService
     - LoggingService
   - Key functions:
     - `select_content_types(intent: str, text: str) -> List[ContentTypeSelection]`
     - `format_response(selected_types: List[ContentTypeSelection], token_info: Dict[str, Any]) -> ContentTypeResponse`

### 2.2 Existing Components to Leverage

1. **AIService** (`app/ai/core/services/ai_core_service.py`)
   - Purpose: Handle LLM API calls
   - Already used by customer intent endpoint

2. **TokenizerService** (`app/ai/core/services/tokenizer_core_service.py`)
   - Purpose: Validate token counts
   - Already used by customer intent endpoint

3. **LoggingService** (`app/shared/logging/`)
   - Purpose: Log requests and responses
   - Already used by customer intent endpoint

## 3. Implementation Steps

### 3.1 Create Data Models

1. Create `app/ai/content_types/models/content_type_model.py`:
   ```python
   from pydantic import BaseModel, Field
   from typing import List, Dict, Any

   class ContentTypeSelection(BaseModel):
       """Model for a selected content type"""
       type: str = Field(..., description="The content type (tutorial, how-to, explanation, reference)")
       confidence: float = Field(..., description="Confidence score for this selection")
       reasoning: str = Field(..., description="Reasoning for this selection")

   class ContentTypeRequest(BaseModel):
       """Request model for content type selection"""
       intent: str = Field(..., description="The customer intent statement")
       text_used: str = Field(..., description="The source text to analyze")

   class ContentTypeResponse(BaseModel):
       """Response model for content type selection"""
       selected_types: List[ContentTypeSelection] = Field(..., description="List of selected content types")
       model: str = Field(..., description="Model used for generation")
       model_family: str = Field(..., description="Family of the model used")
       capabilities: Dict[str, Any] = Field(..., description="Capabilities of the model used")
       usage: Dict[str, int] = Field(..., description="Token usage statistics")
       token_limit: int = Field(..., description="Maximum allowed tokens")
       token_count: int = Field(..., description="Number of tokens used")
       remaining_tokens: int = Field(..., description="Remaining tokens available")
   ```

### 3.2 Implement ContentTypeService

1. Create `app/ai/content_types/services/content_type_service.py`:
   ```python
   from typing import Dict, Any

   class ContentTypeService:
       """Service for creating prompts for content type selection"""
       
       def format_content_type_prompt(self, intent: str, text: str) -> Dict[str, Any]:
           """
           Format the prompt for content type selection
           
           Args:
               intent: The customer intent statement
               text: The source text to analyze
               
           Returns:
               Dictionary containing system message and user message for chat completion
           """
           # Input validation
           if not intent or not intent.strip():
               raise ValueError("Intent cannot be empty")
           if not text or not text.strip():
               raise ValueError("Text cannot be empty")
           
           # System message to set context and behavior
           system_message = """You are an expert at analyzing content and selecting appropriate content types based on the Diátaxis framework.
Your task is to select one or more content types that best match the customer's intent and the source text.

The Diátaxis framework includes four content types:
1. Tutorials: Step-by-step guides for learning by doing
2. How-To Guides: Problem-oriented instructions for accomplished users
3. Explanations: Understanding-oriented background knowledge
4. Reference: Information-oriented technical details

For each selected content type, provide:
1. The type name
2. A confidence score (0.0 to 1.0)
3. Clear reasoning for the selection

Return your response as a JSON object with a "selected_types" array containing objects with "type", "confidence", and "reasoning" fields."""

           # User message with the intent and text
           user_message = f"""Please analyze the following customer intent and source text to select appropriate content types.

Customer Intent:
{intent}

Source Text:
{text}"""

           # Return messages in OpenAI chat format
           return {
               "messages": [
                   {"role": "system", "content": system_message},
                   {"role": "user", "content": user_message}
               ]
           }
   ```

### 3.3 Implement ContentTypeRouter

1. Create `app/ai/content_types/routers/content_type_router.py`:
   ```python
   from fastapi import APIRouter, HTTPException, status, Request
   from app.ai.content_types.models.content_type_model import ContentTypeRequest, ContentTypeResponse, ContentTypeSelection
   from app.ai.content_types.services.content_type_service import ContentTypeService
   from app.ai.core.services.ai_core_service import AIService, OpenAIServiceError
   from app.ai.core.services.tokenizer_core_service import TokenizerService, TokenizerError
   from app.config.settings import OpenAISettings
   from app.shared.logging import get_logger
   import json
   import traceback
   from typing import Dict, Any, List

   # Set up module logger
   logger = get_logger("content_type_router")

   # Define content types based on the Diátaxis framework
   CONTENT_TYPES = {
       "tutorial": {
           "name": "Tutorial",
           "description": "Step-by-step guides for learning by doing",
           "purpose": "To teach users how to accomplish a specific task through hands-on learning with concrete examples",
           "markdown_template": """
# [Title of the Tutorial]

## Introduction
Brief introduction to what the tutorial will cover and why it's important.

## Prerequisites
- What users need to know before starting
- Required tools or software
- Any setup needed

## Step 1: [First Step Title]
Detailed explanation of the first step with code examples or screenshots.

## Step 2: [Second Step Title]
Detailed explanation of the second step with code examples or screenshots.

## Step 3: [Third Step Title]
Detailed explanation of the third step with code examples or screenshots.

## Troubleshooting
Common issues and how to resolve them.

## Next Steps
What to learn next or how to expand on this knowledge.

## Summary
Recap of what was learned in this tutorial.
"""
       },
       "how-to": {
           "name": "How-To Guide",
           "description": "Problem-oriented instructions for accomplished users",
           "purpose": "To provide practical, task-oriented instructions for users who already understand the basics and need to solve a specific problem",
           "markdown_template": """
# How to [Task Name]

## Overview
Brief overview of what this guide will help you accomplish.

## Requirements
- List of requirements or prerequisites
- Any specific versions or configurations needed

## Steps to [Task Name]

### 1. [First Step]
Clear, concise instructions for the first step.

### 2. [Second Step]
Clear, concise instructions for the second step.

### 3. [Third Step]
Clear, concise instructions for the third step.

## Verification
How to verify that the task was completed successfully.

## Troubleshooting
Common issues and their solutions.

## Related Resources
Links to related documentation or resources.
"""
       },
       "explanation": {
           "name": "Explanation",
           "description": "Understanding-oriented background knowledge",
           "purpose": "To provide conceptual understanding and background knowledge about a topic, helping users understand the 'why' behind concepts",
           "markdown_template": """
# Understanding [Topic Name]

## Introduction
Overview of the topic and why understanding it is important.

## What is [Topic Name]?
Clear definition and explanation of the core concept.

## Why is [Topic Name] Important?
Explanation of the significance and relevance of the topic.

## Key Concepts
- **Concept 1**: Explanation of the first key concept
- **Concept 2**: Explanation of the second key concept
- **Concept 3**: Explanation of the third key concept

## How [Topic Name] Works
Detailed explanation of the underlying principles and mechanisms.

## Real-World Applications
Examples of how this concept is applied in practice.

## Common Misconceptions
Addressing common misunderstandings about the topic.

## Further Reading
Resources for deeper exploration of the topic.
"""
       },
       "reference": {
           "name": "Reference",
           "description": "Information-oriented technical details",
           "purpose": "To provide comprehensive, factual information about a topic in a structured format for quick lookup and verification",
           "markdown_template": """
# [Topic Name] Reference

## Overview
Brief overview of what this reference covers.

## Syntax
```
[Code or syntax examples]
```

## Parameters
| Parameter | Type | Description | Required | Default |
|-----------|------|-------------|----------|---------|
| param1    | type | description | Yes/No   | value   |
| param2    | type | description | Yes/No   | value   |

## Return Values
Description of what the function or method returns.

## Examples
```[language]
// Example code
```

## Notes
Important notes or considerations.

## See Also
Links to related reference documentation.
"""
       }
   }

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

   async def select_content_types(intent: str, text: str, req_logger = logger) -> List[ContentTypeSelection]:
       """
       Select content types using AI service
       
       Args:
           intent: The customer intent statement
           text: The source text to analyze
           req_logger: Logger to use for this request
           
       Returns:
           List of selected content types
           
       Raises:
           ContentTypeRouterError: If content type selection fails
       """
       try:
           # Format the prompt
           prompt = content_type_service.format_content_type_prompt(intent, text)
           
           # Generate completion
           completion = await ai_service.generate_completion(
               messages=prompt["messages"],
               model=ai_service.settings.model_config.get("model"),
               temperature=0.2  # Lower temperature for more consistent results
           )
           
           # Parse the response
           try:
               # Extract the JSON response
               response_text = completion.choices[0].message.content
               
               # Parse the JSON
               response_data = json.loads(response_text)
               
               # Convert to ContentTypeSelection objects
               selected_types = []
               for type_data in response_data.get("selected_types", []):
                   selected_types.append(
                       ContentTypeSelection(
                           type=type_data.get("type"),
                           confidence=type_data.get("confidence"),
                           reasoning=type_data.get("reasoning")
                       )
                   )
               
               req_logger.debug(f"Content type selection complete: {selected_types}")
               return selected_types
           except Exception as e:
               req_logger.error(f"Error parsing LLM response: {str(e)}")
               req_logger.error(f"Error type: {type(e)}")
               req_logger.error(f"Error traceback: {traceback.format_exc()}")
               raise ContentTypeRouterError(f"Error parsing LLM response: {str(e)}")
       except Exception as e:
           req_logger.error(f"Error selecting content types: {str(e)}")
           req_logger.error(f"Error type: {type(e)}")
           req_logger.error(f"Error traceback: {traceback.format_exc()}")
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

   @router.post("", response_model=ContentTypeResponse)
   async def select_content_types_endpoint(
       request: Request,
       content_type_request: ContentTypeRequest
   ):
       """
       Select content types based on customer intent and source text
       
       Args:
           request: FastAPI request object
           content_type_request: Content type request
           
       Returns:
           Content type response
       """
       # Get request-specific logger
       req_logger = getattr(request.state, "logger", logger)
       req_logger.info("Content type selection endpoint accessed")
       
       try:
           # Extract intent and text
           intent = content_type_request.intent
           text = content_type_request.text_used
           
           # Validate token count
           token_info = validate_token_count(text, req_logger)
           
           # Select content types
           selected_types = await select_content_types(intent, text, req_logger)
           
           # Format response
           response = format_response(selected_types, token_info, req_logger)
           
           return response
       except ContentTypeRouterError as e:
           req_logger.error(f"Content type router error: {str(e)}")
           raise HTTPException(
               status_code=status.HTTP_400_BAD_REQUEST,
               detail=str(e)
           )
       except Exception as e:
           req_logger.error(f"Unexpected error: {str(e)}")
           req_logger.error(f"Error type: {type(e)}")
           req_logger.error(f"Error traceback: {traceback.format_exc()}")
           raise HTTPException(
               status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
               detail=f"An unexpected error occurred: {str(e)}"
           )
   ```

2. Register router in main FastAPI application in `app/main.py`:
   ```python
   from app.ai.content_types.routers.content_type_router import router as content_type_router

   # Include the Content Type router with proper prefix
   app.include_router(
       content_type_router,
       prefix=API_V1_PREFIX
   )
   ```

### 3.4 Error Handling

1. Define content type-specific exceptions in `app/ai/content_types/exceptions/content_type_exceptions.py`:
   ```python
   class ContentTypeSelectionError(Exception):
       """Custom exception for content type selection errors"""
       pass

   class InvalidContentTypeRequestError(Exception):
       """Custom exception for invalid content type request errors"""
       pass
   ```

### 3.5 Testing

1. Unit tests in `tests/unit/test_content_type.py`:
   ```python
   import pytest
   from app.ai.content_types.services.content_type_service import ContentTypeService
   from app.ai.content_types.models.content_type_model import ContentTypeSelection
   from app.ai.core.services.ai_core_service import AIService
   from app.ai.core.services.tokenizer_core_service import TokenizerService
   from app.config.settings import OpenAISettings
   from unittest.mock import AsyncMock, patch

   # Test data
   test_intent = "As a content creator, I want to schedule posts in advance because it helps me maintain a consistent publishing schedule"
   test_text = "This is a sample document about content scheduling."
   test_response = {
       "selected_types": [
           {
               "type": "how-to",
               "confidence": 0.85,
               "reasoning": "The intent indicates a need for practical instructions on scheduling posts"
           }
       ]
   }

   # Mock AIService
   @pytest.fixture
   def mock_ai_service():
       with patch("app.ai.core.services.ai_core_service.AIService") as mock:
           instance = mock.return_value
           instance.generate_completion = AsyncMock(return_value={
               "choices": [
                   {
                       "message": {
                           "content": '{"selected_types": [{"type": "how-to", "confidence": 0.85, "reasoning": "The intent indicates a need for practical instructions on scheduling posts"}]}'
                       }
                   }
               ]
           })
           yield instance

   # Mock TokenizerService
   @pytest.fixture
   def mock_tokenizer_service():
       with patch("app.ai.core.services.tokenizer_core_service.TokenizerService") as mock:
           instance = mock.return_value
           instance.validate_tokens = lambda text: {
               "token_count": 10,
               "model_limit": 100,
               "tokens_remaining": 90,
               "percentage_used": 10,
               "model": "gpt-4",
               "model_family": "gpt",
               "capabilities": {"supports_functions": True},
               "encoding": "cl100k_base"
           }
           yield instance

   # Test ContentTypeService
   def test_format_content_type_prompt():
       # Create service
       service = ContentTypeService()
       
       # Call method
       result = service.format_content_type_prompt(test_intent, test_text)
       
       # Check result
       assert "messages" in result
       assert len(result["messages"]) == 2
       assert result["messages"][0]["role"] == "system"
       assert result["messages"][1]["role"] == "user"
       assert test_intent in result["messages"][1]["content"]
       assert test_text in result["messages"][1]["content"]
   ```

2. Integration tests in `tests/integration/test_content_type_api.py`:
   ```python
   import pytest
   from fastapi.testclient import TestClient
   from app.main import app
   import json

   # Test data
   test_intent = "As a content creator, I want to schedule posts in advance because it helps me maintain a consistent publishing schedule"
   test_text = "This is a sample document about content scheduling."

   # Create test client
   client = TestClient(app)

   # Test content type selection endpoint
   def test_select_content_types_endpoint():
       # Create request
       request_data = {
           "intent": test_intent,
           "text_used": test_text
       }
       
       # Send request
       response = client.post("/api/v1/content-types", json=request_data)
       
       # Check response
       assert response.status_code == 200
       data = response.json()
       assert "selected_types" in data
       assert len(data["selected_types"]) > 0
       assert "type" in data["selected_types"][0]
       assert "confidence" in data["selected_types"][0]
       assert "reasoning" in data["selected_types"][0]
   ```

## 4. Code Structure

```
app/
├── ai/
│   ├── content_types/
│   │   ├── exceptions/
│   │   │   └── content_type_exceptions.py  # Content type exceptions
│   │   ├── models/
│   │   │   └── content_type_model.py       # Content type models
│   │   ├── routers/
│   │   │   └── content_type_router.py      # Content type router
│   │   └── services/
│   │       └── content_type_service.py      # Content type service
│   ├── core/
│   │   └── services/
│   │       ├── ai_core_service.py           # Existing AI service
│   │       └── tokenizer_core_service.py    # Existing tokenizer service
│   └── customer_intent/
│       └── ...                              # Existing customer intent module
├── shared/
│   └── logging/
│       └── ...                              # Existing logging module
└── main.py                                  # Main application file
```

## 5. Implementation Timeline

### Phase 1: Foundation (Week 1)
- Create data models in `app/ai/content_types/models/content_type_model.py`
- Implement ContentTypeService in `app/ai/content_types/services/content_type_service.py`
- Define content types in the router

### Phase 2: API Implementation (Week 2)
- Implement ContentTypeRouter in `app/ai/content_types/routers/content_type_router.py`
- Add error handling in `app/ai/content_types/exceptions/content_type_exceptions.py`
- Write unit tests in `tests/unit/test_content_type.py`

### Phase 3: Testing & Refinement (Week 3)
- Write integration tests in `tests/integration/test_content_type_api.py`
- Perform end-to-end testing
- Refine based on test results

### Phase 4: Documentation & Deployment (Week 4)
- Update API documentation
- Prepare for deployment
- Create monitoring dashboards

## 6. Dependencies

### 6.1 External Dependencies
- OpenAI/Azure OpenAI API (already in use)
- FastAPI (already in use)
- Pydantic (already in use)

### 6.2 Internal Dependencies
- AIService (`app/ai/core/services/ai_core_service.py`)
- TokenizerService (`app/ai/core/services/tokenizer_core_service.py`)
- LoggingService (`app/shared/logging/`)

## 7. Monitoring & Maintenance

### 7.1 Metrics to Track
- Response time for content type selection
- Token usage per request
- Content type selection distribution
- Error rates by type

### 7.2 Logging
- Log all content type selection requests
- Log LLM responses and reasoning
- Log token usage statistics
- Log errors with detailed context

## 8. Future Enhancements

### 8.1 Short-term
- Add content type validation rules
- Implement confidence threshold configuration
- Add support for custom content type definitions

### 8.2 Long-term
- Develop content type recommendation engine
- Implement content type selection history
- Add content type selection analytics dashboard

## 9. Risks & Mitigation

### 9.1 Risks
- LLM inconsistency in content type selection
- High token usage for large documents
- Performance issues with concurrent requests

### 9.2 Mitigation Strategies
- Implement confidence thresholds
- Add token usage optimization
- Implement request queuing for high load
- Add caching for similar requests

## 10. Success Criteria

### 10.1 Technical Criteria
- Response time < 2 seconds
- 99.9% uptime
- < 1% error rate
- Consistent content type selection

### 10.2 Business Criteria
- Accurate content type selection
- Reduced manual content type determination
- Improved content creation workflow
- Positive user feedback 