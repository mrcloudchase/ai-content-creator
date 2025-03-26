# Document Parser API

A FastAPI application that parses .docx documents and returns their structured content, built using Test-Driven Development principles.

## Features

- Parse .docx documents
- Extract text content while maintaining document structure
- RESTful API with versioning
- Health monitoring endpoint
- Robust error handling and input validation
- Comprehensive test suite

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

#### Error Handling

The API includes robust error handling for:

- Invalid file formats
- Empty documents
- Malformed documents
- Missing files
- Server errors

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── models/              # Data models
│   │   ├── __init__.py
│   │   └── document_models.py
│   ├── routers/             # API routes
│   │   ├── __init__.py
│   │   └── documents.py
│   └── services/            # Business logic
│       ├── __init__.py
│       └── docx_parser.py
├── tests/                   # Tests
│   ├── __init__.py
│   ├── test_api.py          # API endpoint tests
│   └── test_docx_parser.py  # Document parser tests
├── server.py                # Server entry point
├── requirements.txt         # Dependencies
└── README.md                # Documentation
``` 