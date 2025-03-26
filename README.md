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

## Prerequisites

### For Standard Installation
- Python 3.9+ installed

### For Docker Installation
- Docker installed and running (see [Docker installation guide](https://docs.docker.com/get-docker/))
- Docker Compose installed (comes with Docker Desktop for Mac and Windows)

## Installation

### Standard Installation

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

### Docker Installation

1. Ensure Docker is installed and running
2. Clone the repository
3. Build and run the Docker container:

```bash
# Using docker-compose
docker-compose up -d

# Or using newer Docker Compose CLI
docker compose up -d

# View logs
docker compose logs -f
```

#### Using the Helper Script

For convenience, you can use the provided helper script:

```bash
# Make the script executable (first time only)
chmod +x docker-run.sh

# Start the application
./docker-run.sh start

# View all available commands
./docker-run.sh
```

## Running the application

### Standard Method

Start the server:

```bash
python server.py
```

The server will start at http://localhost:8000.

### Using Docker

```bash
# Start the application
docker compose up -d

# Using the helper script
./docker-run.sh start

# Stop the application
docker compose down
# or
./docker-run.sh stop
```

The server will be accessible at http://localhost:8000.

## Running Tests

### Standard Method

Run the comprehensive test suite:

```bash
pytest
```

For detailed test output:

```bash
pytest -v
```

### Using Docker

```bash
# Run tests
docker compose exec api pytest
# or
./docker-run.sh test

# Run tests with verbose output
docker compose exec api pytest -v
# or
./docker-run.sh test-v
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
├── Dockerfile               # Docker image definition
├── docker-compose.yml       # Docker Compose configuration
├── docker-run.sh            # Helper script for Docker operations
├── server.py                # Server entry point
├── requirements.txt         # Dependencies
└── README.md                # Documentation
``` 