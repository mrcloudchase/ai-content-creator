# Document Parser & AI API

A FastAPI application that parses .docx documents and generates AI completions using OpenAI, built using Test-Driven Development principles.

## Features

- Parse .docx documents
- Extract text content while maintaining document structure
- Generate AI completions using OpenAI API
- Count tokens for text to assess OpenAI model compatibility
- Automatic token limit validation
- JSON-structured document output ready for AI integration
- RESTful API with versioning
- Health monitoring endpoint
- Robust error handling and input validation
- Comprehensive test suite
- Environment-based configuration

## Development Approach

This application follows Test-Driven Development (TDD) principles:

1. Tests are written before implementation
2. Code includes assertions that halt execution if critical conditions aren't met
3. Edge cases are thoroughly tested
4. Continuous validation through an extensive test suite

## Installation

1. Clone the repository
2. Create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configure environment variables:

Create a `.env` file based on the provided `.env-example`:

```
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
OPENAI_ORGANIZATION=your_openai_org_id  # Optional
OPENAI_DEFAULT_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=1000
OPENAI_TEMPERATURE=0.7

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

## Running the application

Start the server:

```bash
python server.py
```

The server will start at http://localhost:8000.

## Running Tests

Run the comprehensive test suite:

```bash
pytest
```

For detailed test output:

```bash
pytest -v
```

## API Endpoints

### Service Information

`GET /`

Returns basic information about the API.

### Health Check

`GET /health`

Returns the health status of the service.

### Extract Document Text

`POST /api/v1/documents/extract-text`

Upload a .docx file to extract its text content. The endpoint returns a JSON object with a "document" field containing the extracted text. This format is designed for direct integration with the AI completions endpoint.

The endpoint automatically checks token count against your configured `OPENAI_MAX_TOKENS` limit and returns an appropriate error if the document is too large.

#### Request

- Content-Type: multipart/form-data
- Body:
  - file: .docx file to parse

#### Response

JSON object containing the parsed document text:

```json
{
  "document": "The extracted text content from the document with all paragraphs, headings, lists, and tables preserved."
}
```

The output includes:
- Document text
- Paragraphs
- Headings
- Lists (with bullet/numbering preserved)
- Tables (formatted as text)

#### Error Responses

- **413 Request Entity Too Large**: Returned when the document's token count exceeds the configured `OPENAI_MAX_TOKENS` limit. The response includes the actual token count and the configured limit.

```json
{
  "detail": "Document exceeds token limit: 2500 tokens (limit: 1000). Use the token counting endpoint for more information.",
  "error_type": "token_limit_exceeded"
}
```

### Generate AI Completion

`POST /api/v1/ai/completions`

Send a prompt to OpenAI to generate a completion.

#### Request

- Content-Type: application/json
- Body:
  ```json
  {
    "prompt": "Your text prompt here",
    "model": "gpt-3.5-turbo",  // Optional, defaults to configured model
    "max_tokens": 500,         // Optional, defaults to 1000
    "temperature": 0.7         // Optional, defaults to 0.7
  }
  ```

#### Response

JSON object containing the generated text and usage statistics:

```json
{
  "text": "Generated text response from OpenAI",
  "model": "gpt-3.5-turbo",
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 100,
    "total_tokens": 110
  }
}
```

### Count Tokens

`POST /api/v1/tokens/count`

Count the number of tokens in a text string to check compatibility with OpenAI models.

#### Request

- Content-Type: application/json
- Body:
  ```json
  {
    "text": "Your text to count tokens for",
    "model": "gpt-3.5-turbo"  // Optional, defaults to gpt-3.5-turbo
  }
  ```

#### Response

JSON object containing token count and context information:

```json
{
  "token_count": 5,
  "model": "gpt-3.5-turbo",
  "model_limit": 4096,
  "percentage_used": 0.12,
  "tokens_remaining": 4091,
  "is_near_limit": false,
  "exceeds_limit": false
}
```

#### Error Handling

All APIs include robust error handling for:

- Invalid input formats
- Empty input
- Service unavailability 
- Server errors

## Common Workflow

A typical workflow might include:

1. Parse a document using the `extract-text` endpoint
   - If the document is too large, you'll receive a 413 error with token information
   - If successful, you'll get a JSON response with a `document` field containing the parsed text
2. Extract the `document` field from the response and send it as the `prompt` in a request to the `ai/completions` endpoint
3. For debugging or to check token usage, use the `tokens/count` endpoint separately

### Integration Example

```python
import requests

# 1. Parse the document
with open('example.docx', 'rb') as f:
    parse_response = requests.post(
        'http://localhost:8000/api/v1/documents/extract-text',
        files={'file': f}
    )

if parse_response.status_code == 200:
    # 2. Extract the document text
    document_text = parse_response.json()['document']
    
    # 3. Send to AI endpoint
    ai_response = requests.post(
        'http://localhost:8000/api/v1/ai/completions',
        json={'prompt': document_text}
    )
    
    # 4. Process AI response
    if ai_response.status_code == 200:
        ai_result = ai_response.json()
        print(f"AI Response: {ai_result['text']}")
```

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI application
│   ├── config/                  # Configuration
│   │   ├── __init__.py
│   │   └── settings.py          # Environment settings
│   ├── models/                  # Data models
│   │   ├── __init__.py
│   │   ├── document_models.py   # Document schemas
│   │   ├── ai_models.py         # AI completion schemas
│   │   └── token_models.py      # Token counting schemas
│   ├── routers/                 # API routes
│   │   ├── __init__.py
│   │   ├── documents.py         # Document endpoints
│   │   ├── ai.py                # AI endpoints
│   │   └── tokens.py            # Token counting endpoints
│   └── services/                # Business logic
│       ├── __init__.py
│       ├── docx_parser.py       # Document parsing logic
│       ├── openai_service.py    # OpenAI integration
│       └── token_service.py     # Token counting logic
├── tests/                       # Tests
│   ├── __init__.py
│   ├── conftest.py              # Test configuration
│   ├── test_api.py              # Document API tests
│   ├── test_docx_parser.py      # Parser tests
│   ├── test_ai_api.py           # AI API tests
│   ├── test_openai_service.py   # OpenAI service tests
│   ├── test_token_api.py        # Token API tests
│   ├── test_token_service.py    # Token service tests
│   ├── test_token_limits.py     # Token limit tests
│   └── test_integration.py      # Integration tests
├── server.py                    # Server entry point
├── requirements.txt             # Dependencies
├── .env-example                 # Example environment file
├── pytest.ini                   # Test configuration
└── README.md                    # Documentation
```

## GitHub Repository

The code is available at: https://github.com/mrcloudchase/docx-parser-api.git 