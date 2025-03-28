# Technical Architecture - Document Parser & AI API

## 1. Overview

The Document Parser & AI API is a modular Python application built with FastAPI that provides document parsing capabilities and AI-powered text processing services. The application follows a clean, service-oriented architecture with clear separation of concerns, robust error handling, and comprehensive test coverage.

Key features:
- Document parsing (.docx files)
- Text extraction with structure preservation
- Token counting for OpenAI models
- OpenAI API integration for text completion
- Customer intent generation from document content with user-type customization

## 2. File Structure

The application follows a modular structure organized by feature:

```
/
│
├──app/
│   ├──models/
│   │       ├──__init__.py
│   │       ├──ai_models.py                # Models for AI requests/responses
│   │       ├──customer_intent_models.py   # Models for customer intent functionality
│   │       ├──document_models.py          # Models for document parsing
│   │       └──token_models.py             # Models for token counting
│   │
│   ├──routers/
│   │       ├──__init__.py
│   │       ├──ai.py                       # AI completion endpoint router
│   │       ├──customer_intent.py          # Customer intent router wrapper
│   │       ├──documents.py                # Document parsing router
│   │       └──tokens.py                   # Token counting router
│   │
│   ├──services/
│   │       ├──__init__.py
│   │       ├──customer_intent_service.py  # Service for generating customer intents
│   │       ├──docx_parser.py              # Service for parsing .docx documents
│   │       ├──openai_service.py           # Service for OpenAI API integration
│   │       └──token_service.py            # Service for token counting
│   │
│   ├──config/
│   │       └── settings.py                # Application configuration
│   │
│   ├──main.py                             # Application entry point
│   └──__init__.py                         # Package initialization
│
├──tests/
│   ├──__init__.py
│   ├──conftest.py                         # Configure tests location for pytest
│   ├──test_ai_api.py                      # Tests for AI API
│   ├──test_customer_intent_api.py         # Tests for customer intent API
│   ├──test_document_api.py                # Tests for document API
│   ├──test_docx_parser_service.py         # Tests for document parser service
│   ├──test_integration.py                 # Integration tests
│   ├──test_openai_service.py              # Tests for OpenAI service
│   ├──test_token_api.py                   # Tests for token API
│   ├──test_token_limits.py                # Tests for token limit handling
│   └──test_token_service.py               # Tests for token service
│
│
│
├──server.py                               # Server initialization script 
├──test_customer_intent.py                 # End-to-end test for customer intent
├──test_full_prd.py                        # End-to-end test with complex PRD document
├──pytest.ini                              # Pytest configuration
├──requirements.txt                        # Project dependencies
├──.env-example                            # Environment variables template
├──README.md                               # Project documentation
```

## 3. API Architecture

The application uses FastAPI with API versioning and follows RESTful design principles.

### 3.1 API Structure

- Base URL: `/api/v1`
- Health check endpoint: `/health`
- API information: `/`

### 3.2 Endpoints

#### Document Endpoints
- `POST /api/v1/documents/extract-text`: Extract text from a .docx document
  - Input: .docx file
  - Output: JSON with extracted text in `document` field

#### Token Endpoints
- `POST /api/v1/tokens/count`: Count tokens in a text
  - Input: Text to count tokens in
  - Output: Token count, model limit, percentage used

#### AI Endpoints
- `POST /api/v1/ai/completions`: Generate text completion using OpenAI
  - Input: Prompt, optional parameters (max_tokens, temperature)
  - Output: Generated text, model used, token usage

#### Customer Intent Endpoints
- `POST /api/v1/customer-intent/generate`: Generate a customer intent statement
  - Input: Document text, optional user type, and parameters (max_tokens, temperature)
  - Output: Generated customer intent statement, model, token usage
  - Supports customization based on user type (e.g., admin, regular user)

## 4. Component Architecture

### 4.1 Request Flow

The application follows a standard flow:
1. HTTP request received by FastAPI router
2. Request validation using Pydantic models
3. Business logic handled by service layer
4. Response transformation and validation
5. HTTP response returned to client

### 4.2 Error Handling

- Custom exception types for different error categories (e.g., OpenAIServiceError)
- Consistent HTTP status codes (413 for token limit exceeded, 503 for service unavailable)
- Detailed error messages without exposing sensitive information
- Logging for debugging and monitoring

## 5. Service Architecture

### 5.1 Document Parser Service

- Parses .docx files and extracts text
- Preserves document structure (headings, tables, lists)
- Handles special characters for JSON compatibility
- Validates token limits for API usage

### 5.2 OpenAI Service

- Async communication with OpenAI API
- Configurable model and parameters
- Error handling for API failures
- Token usage tracking

### 5.3 Token Service

- Accurate token counting for OpenAI models
- Token limit validation
- Percentage calculations for token usage
- Threshold warnings for approaching limits

### 5.4 Customer Intent Service

- Generates customer intent statements from document text
- Customizable by user type (e.g., admin, regular user)
- Uses OpenAI service for text generation
- Proper prompt engineering to extract user stories in "As a [user], I want to [action] because [reason]" format

## 6. Code Patterns and Design Principles

### 6.1 Dependency Injection

Services are injected into routers, promoting:
- Testability through mocking
- Loose coupling between components
- Better separation of concerns

### 6.2 Repository Pattern

Clear separation between:
- API layer (routers)
- Business logic (services)
- Data models (Pydantic models)

### 6.3 Async/Await Pattern

- Async endpoints for improved concurrency
- Proper awaiting of async operations
- Efficient handling of I/O-bound operations (especially important for OpenAI API calls)

### 6.4 Validation

- Input validation using Pydantic models
- Output validation to ensure consistent responses
- Assertions for internal logic validation

## 7. Testing Strategy

### 7.1 Test Categories

- Unit tests: Test individual components in isolation
- Integration tests: Test interaction between components
- End-to-end tests: Test complete workflows using realistic PRD documents

### 7.2 Test Tools

- Pytest for test framework
- AsyncMock for mocking async functions
- FastAPI TestClient for API testing
- Coverage reporting

### 7.3 Test Coverage

- All services have dedicated test files
- All API endpoints have test coverage
- Edge cases and error conditions are tested
- End-to-end testing with realistic PRD documents

## 8. Environment Configuration

- Environment-based configuration using dotenv
- OpenAI API settings (API key, org ID, default model)
- Server configuration (host, port)
- Runtime parameters (max tokens, temperature)

## 9. Future Considerations

- Additional document formats (PDF, etc.)
- More advanced AI capabilities and fine-tuning
- Performance optimizations for large documents
- Additional user-specific features
- Enhanced security features
- Batch processing capabilities 