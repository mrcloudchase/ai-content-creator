# AI Content Creator

A FastAPI backend for processing documents and generating AI-powered customer intent statements based on document input.

## Table of Contents

- [Overview](#overview)
- [For API Consumers](#for-api-consumers)
  - [API Endpoints](#api-endpoints)
  - [Using the Customer Intent Endpoint](#using-the-customer-intent-endpoint)
  - [API Response Format](#api-response-format)
  - [Error Handling](#error-handling)
  - [Using cURL](#using-curl)
  - [Python Client Example](#python-client-example)
- [For Developers](#for-developers)
  - [Project Structure](#project-structure)
  - [Execution Flow](#execution-flow)
  - [Development Setup](#development-setup)
  - [Running the Application](#running-the-application)
  - [Testing](#testing)
  - [Adding New File Types](#adding-new-file-types)

## Overview

This application processes document files (.docx, .md, .txt) and leverages OpenAI's models to generate customer intent statements in the format: "As a [user type], I want to [action] because [reason]". The application handles file upload, text extraction, token validation, and AI content generation in a seamless workflow.

---

## For API Consumers

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information with available endpoints |
| GET | `/health` | Health check endpoint for monitoring |
| POST | `/api/v1/customer-intent` | Generate customer intent from document |

### Using the Customer Intent Endpoint

Send a POST request to `/api/v1/customer-intent` with a file in the request body:
- Content-Type: `multipart/form-data`
- Form field name: `file`
- Supported file types: `.docx`, `.md`, `.txt`

### API Response Format

Successful response (200 OK):
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

### Error Handling

| Status Code | Description | Resolution |
|-------------|-------------|------------|
| 400 | Bad Request - Invalid input | Check file format and contents |
| 413 | Request Entity Too Large | Document exceeds token limit, use shorter document |
| 415 | Unsupported Media Type | Use a supported file type (.docx, .md, .txt) |
| 500 | Internal Server Error | Server issue, retry later |

### Using cURL

You can use cURL to test the API from the command line:

```bash
curl -X POST \
  -F "file=@/path/to/your/document.docx" \
  https://your-app-name.azurewebsites.net/api/v1/customer-intent
```

Where:
- `-X POST` specifies the HTTP method
- `-F "file=@/path/to/your/document.docx"` uploads the file as form data
- Replace `/path/to/your/document.docx` with the actual path to your document
- Replace `https://your-app-name.azurewebsites.net` with your deployed API URL

For local testing, use:

```bash
curl -X POST \
  -F "file=@/path/to/your/document.docx" \
  http://localhost:8000/api/v1/customer-intent
```

To save the response to a file:

```bash
curl -X POST \
  -F "file=@/path/to/your/document.docx" \
  http://localhost:8000/api/v1/customer-intent \
  -o response.json
```

### Python Client Example

```python
import requests

def generate_customer_intent(file_path, api_url):
    """
    Generate customer intent by uploading a document to the API
    
    Args:
        file_path: Path to the document file (.docx, .md, or .txt)
        api_url: Base URL of the deployed API
    
    Returns:
        Dictionary containing the customer intent and metadata
    """
    # API endpoint
    endpoint = f"{api_url}/api/v1/customer-intent"
    
    # Open the file in binary mode
    with open(file_path, 'rb') as file:
        # Create the files dictionary for multipart/form-data upload
        files = {
            'file': (file.name, file, 'application/octet-stream')
        }
        
        # Make the POST request
        response = requests.post(endpoint, files=files)
    
    # Raise an exception for HTTP errors
    response.raise_for_status()
    
    # Return the JSON response
    return response.json()

# Example usage
if __name__ == "__main__":
    # Replace with your API URL (Azure App Service or other hosting)
    api_url = "https://your-app-name.azurewebsites.net"
    
    # File to upload
    document_path = "path/to/document.docx"
    
    try:
        # Call the API
        result = generate_customer_intent(document_path, api_url)
        
        # Print the generated intent
        print(f"Customer Intent: {result['intent']}")
        print(f"Model used: {result['model']}")
        print(f"Token usage: {result['usage']}")
        
    except requests.exceptions.HTTPError as e:
        print(f"API request failed: {e}")
        if e.response.status_code == 413:
            print("Document exceeds token limit. Try a smaller document.")
        elif e.response.status_code == 415:
            print("Unsupported file type. Use .docx, .md, or .txt files.")
    except Exception as e:
        print(f"Error: {e}")
```

---

## For Developers

### Project Structure

The project follows a feature-based organization:

```
/
├── app/
│   ├── config/
│   │   └── settings.py                  # Application configuration
│   ├── input_processing/
│   │   ├── core/
│   │   │   ├── services/
│   │   │   │   ├── file_handler_routing_logic_core_services.py
│   │   │   │   └── input_processing_core_service.py
│   │   ├── markdown/
│   │   │   ├── services/
│   │   │   │   └── markdown_service.py  # Markdown processing
│   │   ├── docx/
│   │   │   ├── services/
│   │   │   │   └── docx_service.py      # DOCX processing
│   │   └── txt/
│   │       ├── services/
│   │           └── txt_service.py       # TXT processing
│   ├── ai/
│   │   ├── core/
│   │   │   ├── services/
│   │   │   │   ├── ai_core_service.py   # Core AI service for OpenAI
│   │   │   │   └── tokenizer_core_service.py # Token counting
│   │   └── customer_intent/
│   │       ├── models/
│   │       │   └── ai_customer_intent_model.py # Request/response models
│   │       ├── routers/
│   │       │   └── ai_customer_intent_router.py # Customer intent endpoint
│   │       ├── services/
│   │       │   └── ai_customer_intent_service.py # Intent prompt structure
│   ├── shared/
│   │   └── logging.py                   # Logging configuration
│   ├── main.py                          # Application entry point
├── tests/                               # Test suite
├── server.py                            # Server startup
├── requirements.txt                     # Dependencies
└── .env-example                         # Environment template
```

### Execution Flow

When a file is uploaded to the API endpoint, the following execution sequence occurs:

1. **server.py** - Server startup file that imports and runs the FastAPI app
2. **app/main.py** - Entry point that defines routes and receives the initial request
3. **app/ai/customer_intent/routers/ai_customer_intent_router.py** - Handles the request and orchestrates the processing flow
4. **File Type Detection & Processing**:
   - **app/input_processing/core/services/file_handler_routing_logic_core_services.py** - Identifies file type
   - Based on file type, one of:
     - **app/input_processing/docx/services/docx_service.py** 
     - **app/input_processing/markdown/services/markdown_service.py**
     - **app/input_processing/txt/services/txt_service.py**
5. **Text Processing**:
   - **app/input_processing/core/services/input_processing_core_service.py** - Cleans and standardizes text
6. **Token Validation**:
   - **app/ai/core/services/tokenizer_core_service.py** - Counts tokens and checks limits
   - **app/config/settings.py** - Provides model configuration for token limits
7. **AI Processing**:
   - **app/ai/customer_intent/services/ai_customer_intent_service.py** - Creates the prompt structure
   - **app/ai/core/services/ai_core_service.py** - Communicates with OpenAI API
8. **Response Formatting**:
   - **app/ai/customer_intent/models/ai_customer_intent_model.py** - Defines the response structure

### Development Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd ai-content-creator
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env-example .env
   ```
   
   Edit the `.env` file with your OpenAI API key and other settings:
   ```
   OPENAI_API_KEY=your_api_key_here
   OPENAI_DEFAULT_MODEL=gpt-4  # Or your preferred model
   OPENAI_TEMPERATURE=0.7
   
   # Logging Configuration
   APP_LOGGING_LOG_LEVEL=info
   APP_LOGGING_LOG_TO_CONSOLE=true
   APP_LOGGING_LOG_TO_FILE=false
   APP_LOGGING_LOG_DIR=logs
   APP_LOGGING_LOG_FILE_NAME=ai_content_developer.log
   APP_LOGGING_MAX_LOG_FILE_SIZE_MB=5
   APP_LOGGING_BACKUP_COUNT=3
   ```

### Running the Application

Start the development server:
```bash
python server.py
```

The API will be available at:
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- Health check: http://localhost:8000/health

The server will automatically reload when code changes are detected, thanks to the `reload=True` parameter in server.py.

### Testing

Run the test suite:
```bash
pytest
```

For verbose output:
```bash
pytest -v
```

### Adding New File Types

To add support for a new file type:

1. Create a new module in the appropriate directory:
   ```
   app/input_processing/new_format/
   ├── __init__.py
   ├── models/
   ├── routers/
   └── services/
       └── new_format_service.py
   ```

2. Implement the `extract_text` method in the service:
   ```python
   class NewFormatService:
       @staticmethod
       def extract_text(file_content: bytes) -> str:
           # Implementation for extracting text from the new format
           ...
           return extracted_text
   ```

3. Update the file type router in `app/input_processing/core/services/file_handler_routing_logic_core_services.py`:
   ```python
   FILE_EXTENSIONS_DICT = {
       # Existing formats...
       ".new": "new_format",
   }
   ```

4. Add the new service to the router in `app/ai/customer_intent/routers/ai_customer_intent_router.py`:
   ```python
   from app.input_processing.new_format.services.new_format_service import NewFormatService
   
   # Initialize services
   new_format_service = NewFormatService()
   
   # In extract_file_content function:
   elif file_type == "new_format":
       return new_format_service.extract_text(file_content)
   ```

5. Add tests for the new file type in the `tests/` directory.

---

This README provides comprehensive guidance for both API consumers and developers. For any additional information or assistance, please contact the repository maintainers. 