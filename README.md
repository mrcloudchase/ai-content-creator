# Document Parser & AI API

A FastAPI application that parses .docx documents and generates AI completions using OpenAI, built using Test-Driven Development principles.

## Features

- Parse .docx documents
- Extract text content while maintaining document structure
- Generate AI completions using OpenAI API
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

Upload a .docx file to extract its text content.

#### Request

- Content-Type: multipart/form-data
- Body:
  - file: .docx file to parse

#### Response

Plain text content extracted from the document, including:

- Document text
- Paragraphs
- Headings
- Lists (with bullet/numbering preserved)
- Tables (formatted as text)

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

#### Error Handling

Both APIs include robust error handling for:

- Invalid input formats
- Empty input
- Service unavailability 
- Server errors

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
│   │   └── ai_models.py         # AI completion schemas
│   ├── routers/                 # API routes
│   │   ├── __init__.py
│   │   ├── documents.py         # Document endpoints
│   │   └── ai.py                # AI endpoints
│   └── services/                # Business logic
│       ├── __init__.py
│       ├── docx_parser.py       # Document parsing logic
│       └── openai_service.py    # OpenAI integration
├── tests/                       # Tests
│   ├── __init__.py
│   ├── conftest.py              # Test configuration
│   ├── test_api.py              # Document API tests
│   ├── test_docx_parser.py      # Parser tests
│   ├── test_ai_api.py           # AI API tests
│   └── test_openai_service.py   # OpenAI service tests
├── server.py                    # Server entry point
├── requirements.txt             # Dependencies
├── .env-example                 # Example environment file
├── pytest.ini                   # Test configuration
└── README.md                    # Documentation
```

## GitHub Repository

The code is available at: https://github.com/mrcloudchase/docx-parser-api.git 