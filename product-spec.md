# AI Content Creator - Product Requirements Document

## 1. Introduction

### 1.1 Purpose
The AI Content Creator is a FastAPI-based backend service designed to process documents and generate AI-powered customer intent statements. The system analyzes uploaded documents and converts them into structured user stories following the format: "As a [user type], I want to [action] because [reason]".

### 1.2 Scope
This document outlines the functional and non-functional requirements for the AI Content Creator system, including its core features, technical specifications, and deployment requirements.

### 1.3 Target Audience
- API Consumers: Developers and applications needing to generate customer intent statements
- System Administrators: Teams responsible for deployment and maintenance
- Developers: Engineers working on the system's implementation and extensions

## 2. Product Overview

### 2.1 Product Vision
To provide a robust, scalable, and secure API service that automates the generation of customer intent statements from various document formats, helping teams better understand user needs and requirements.

### 2.2 Key Features
1. Document Processing
   - Support for multiple file formats (.docx, .md, .txt)
   - Automated text extraction and cleaning
   - Token validation and management

2. AI-Powered Analysis
   - Integration with OpenAI/Azure OpenAI
   - Structured customer intent generation
   - Content type selection based on Diátaxis framework
   - Token usage optimization

3. API Interface
   - RESTful endpoints
   - Comprehensive error handling
   - Detailed response metadata

4. Deployment Options
   - Docker containerization
   - Azure App Service deployment
   - Local development environment

## 3. Functional Requirements

### 3.1 Document Processing
#### FR-1: File Upload
- System must accept file uploads via multipart/form-data
- Supported file types: .docx, .md, .txt
- Maximum file size based on token limits

#### FR-2: Text Extraction
- Extract text content from .docx files
- Parse markdown content from .md files
- Process plain text from .txt files
- Clean and standardize extracted text

#### FR-3: Token Management
- Count tokens in input text
- Validate against model limits
- Track token usage and remaining quota

### 3.2 AI Processing
#### FR-4: Intent Generation
- Generate customer intent statements
- Follow format: "As a [user type], I want to [action] because [reason]"
- Use OpenAI/Azure OpenAI for processing

#### FR-5: Content Type Selection
- Analyze customer intent and source text
- Match against Diátaxis framework content types
- Select appropriate content types based on context
- Support multiple content type selection when applicable
- Provide reasoning for content type selection

#### FR-6: Response Formatting
- Return structured JSON responses
- Include metadata about processing
- Provide usage statistics

### 3.3 API Interface
#### FR-7: Endpoints
- Health check endpoint
- Customer intent generation endpoint
- Content type selection endpoint
- API documentation endpoint

#### FR-8: Error Handling
- Validate input files
- Handle processing errors
- Return appropriate HTTP status codes

## 4. Non-Functional Requirements

### 4.1 Performance
- Response time: < 5 seconds for standard documents
- Concurrent request handling
- Token processing optimization

### 4.2 Security
- Secure API key management
- Input validation
- Rate limiting
- CORS configuration

### 4.3 Scalability
- Container-based deployment
- Horizontal scaling support
- Resource optimization

### 4.4 Reliability
- Error recovery
- Logging and monitoring
- Health checks

### 4.5 Maintainability
- Modular code structure
- Comprehensive documentation
- Test coverage

## 5. Technical Specifications

### 5.1 Technology Stack
- Python 3.12+
- FastAPI framework
- OpenAI/Azure OpenAI integration
- Docker containerization

### 5.2 API Specifications
#### Endpoints
1. GET /
   - Purpose: API information
   - Response: Available endpoints and documentation

2. GET /health
   - Purpose: Health check
   - Response: System status

3. POST /api/v1/customer-intent
   - Purpose: Generate customer intent
   - Input: Multipart form data with file
   - Response: JSON with intent and metadata

4. POST /api/v1/content-types
   - Purpose: Select appropriate content types using LLM analysis
   - Input: JSON with intent and source text
   - Response: JSON with selected content types and reasoning
   - Process: Uses LLM to analyze intent and text to determine most appropriate content types
   - Features:
     - LLM-based analysis of user intent and context
     - Confidence scoring for each selected content type
     - Detailed reasoning for content type selection
     - Support for multiple content type selection when appropriate

### 5.3 Response Format
#### Customer Intent Response
```json
{
  "intent": "As a [user type], I want to [action] because [reason]",
  "model": "gpt-4",
  "model_family": "gpt",
  "capabilities": {
    "supports_functions": true,
    "supports_vision": false,
    "supports_embeddings": true
  },
  "usage": {
    "prompt_tokens": 123,
    "completion_tokens": 45,
    "total_tokens": 168
  },
  "token_limit": 8192,
  "token_count": 1234,
  "remaining_tokens": 6958,
  "text_used": "Text content used to generate the intent..."
}
```

#### Content Type Selection Response
```json
{
  "selected_types": [
    {
      "type": "tutorial",
      "confidence": 0.85,
      "reasoning": "The intent indicates a learning need with step-by-step guidance requirement"
    },
    {
      "type": "how-to",
      "confidence": 0.75,
      "reasoning": "The user needs practical instructions for a specific task"
    }
  ],
  "model": "gpt-4",
  "model_family": "gpt",
  "usage": {
    "prompt_tokens": 234,
    "completion_tokens": 89,
    "total_tokens": 323
  },
  "token_limit": 8192,
  "token_count": 2345,
  "remaining_tokens": 5847
}
```

### 5.4 Content Type Definitions
The system will use the Diátaxis framework's four content types, with LLM-powered selection based on the following criteria:

1. Tutorials
   - Learning-oriented
   - Step-by-step guidance
   - Hands-on examples
   - LLM Selection Criteria: When the intent indicates a need for learning or understanding a new concept

2. How-To Guides
   - Problem-oriented
   - Practical instructions
   - Specific tasks
   - LLM Selection Criteria: When the intent focuses on solving a specific problem or completing a task

3. Technical Reference
   - Information-oriented
   - Detailed specifications
   - API documentation
   - LLM Selection Criteria: When the intent requires detailed technical information or API specifications

4. Explanations
   - Understanding-oriented
   - Background context
   - Conceptual overview
   - LLM Selection Criteria: When the intent seeks to understand concepts or background information

The LLM will analyze the following aspects when selecting content types:
- User's primary goal from the intent statement
- Context and complexity level indicated in the source text
- Specific requirements or constraints mentioned
- Target audience's technical expertise level
- Whether the content needs to be task-focused or concept-focused

## 6. Deployment Requirements

### 6.1 Container Requirements
- Docker support
- Platform: linux/amd64
- Port: 80 (internal)
- Environment variables configuration

### 6.2 Azure Deployment
- App Service configuration
- Managed Identity support
- ACR integration
- Environment-specific settings

### 6.3 Local Development
- Python virtual environment
- Development server
- Environment variable management
- Testing framework

## 7. Future Enhancements

### 7.1 Planned Features
- Additional file format support
- Batch processing capabilities
- Enhanced error reporting
- Custom model fine-tuning
- Advanced content type selection algorithms
- Content type recommendation engine
- Content type validation rules

### 7.2 Integration Opportunities
- CI/CD pipeline integration
- Monitoring system integration
- Analytics dashboard
- User management system

## 8. Success Metrics

### 8.1 Performance Metrics
- Response time < 5 seconds
- 99.9% uptime
- < 1% error rate

### 8.2 Business Metrics
- Number of processed documents
- Token usage efficiency
- User satisfaction with generated intents

## 9. Constraints and Limitations

### 9.1 Technical Constraints
- Token limits based on model
- File size restrictions
- API rate limits

### 9.2 Business Constraints
- OpenAI/Azure OpenAI costs
- Resource utilization
- Compliance requirements

## 10. Appendix

### 10.1 Glossary
- Token: Unit of text processing for AI models
- Intent: Structured user requirement statement
- Managed Identity: Azure authentication method
- Diátaxis Framework: A framework for documentation that categorizes content into four types: tutorials, how-to guides, technical reference, and explanations

### 10.2 References
- OpenAI API Documentation
- Azure App Service Documentation
- FastAPI Documentation 