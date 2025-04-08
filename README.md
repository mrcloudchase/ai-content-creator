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
  - [Requirements](#requirements)
  - [Project Structure](#project-structure)
  - [Execution Flow](#execution-flow)
  - [Development Setup](#development-setup)
  - [Running the Application](#running-the-application)
  - [Azure OpenAI Integration](#azure-openai-integration)
  - [Testing](#testing)
  - [Adding New File Types](#adding-new-file-types)
- [Containerization & Deployment](#containerization-deployment)
  - [Building the Docker Container](#building-the-docker-container)
  - [Running Locally with Docker](#running-locally-with-docker)
  - [Deploying to Azure App Service](#deploying-to-azure-app-service)
  - [Troubleshooting](#troubleshooting)

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
  https://url/api/v1/customer-intent
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

### Requirements

- **Python 3.12+** - Required for compatibility with tiktoken and other dependencies
- OpenAI API key
- pip package manager

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

1. **Ensure Python 3.12+ is installed**:
   ```bash
   python --version  # Should show Python 3.12.x or higher
   ```
   If not installed, download from [python.org](https://www.python.org/downloads/) or use your operating system's package manager.

2. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd ai-content-creator
   ```

3. **Create a virtual environment with Python 3.12**:
   ```bash
   python3.12 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**:
   ```bash
   cp .env-example .env
   ```
      # ===== Configuration Toggle =====
   # To switch between OpenAI and Azure OpenAI:
   # 1. Comment out the section you DON'T want to use (add # at the beginning of each line)
   # 2. Uncomment the section you DO want to use (remove # from the beginning of each line)
   # 3. Restart the application after changing the configuration

   # ===== Standard OpenAI Configuration =====
   # Uncomment these settings to use standard OpenAI
   OPENAI_API_KEY=sk-your-api-key-here
   OPENAI_ORGANIZATION=org-your-org-id-here  # Optional

   # ===== Azure OpenAI Configuration =====
   # Uncomment these settings to use Azure OpenAI with managed identity
   # AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
   # AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name
   # AZURE_OPENAI_API_VERSION=2023-12-01-preview

   # ===== Shared Settings =====
   # These settings apply to both OpenAI and Azure OpenAI
   DEFAULT_MODEL=gpt-4  # Used for both OpenAI and for tokenization estimation with Azure
   MAX_TOKENS=4000
   TEMPERATURE=0.7

   # ===== Application Settings =====
   # Server configuration
   HOST=0.0.0.0
   PORT=8000

   # Logging configuration
   LOG_LEVEL=INFO
   LOG_FORMAT=json
   APP_LOGGING_LOG_LEVEL=info
   APP_LOGGING_LOG_TO_CONSOLE=true
   APP_LOGGING_LOG_TO_FILE=false
   APP_LOGGING_LOG_DIR=logs
   APP_LOGGING_LOG_FILE_NAME=ai_content_developer.log
   APP_LOGGING_MAX_LOG_FILE_SIZE_MB=5
   APP_LOGGING_BACKUP_COUNT=3
   ```

### Running the Application

1. Start the application using:
```bash
python server.py
```

2. Access the API documentation at `http://localhost:8000/docs`

3. To deploy to production, you can containerize using the provided Dockerfile or deploy directly to Azure App Service.

### Azure OpenAI Integration

The application supports both standard OpenAI API and Azure OpenAI Service with managed identity authentication.

#### Configuring Azure OpenAI

To use Azure OpenAI with managed identity:

1. Comment out the standard OpenAI configuration in your `.env` file
2. Uncomment the Azure OpenAI configuration section
3. Update with your Azure OpenAI details:
   ```
   # Standard OpenAI (commented out)
   # OPENAI_API_KEY=sk-your-api-key-here
   # OPENAI_ORGANIZATION=org-your-org-id-here

   # Azure OpenAI (uncommented)
   AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
   AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name
   AZURE_OPENAI_API_VERSION=2023-12-01-preview
   ```

4. Restart the application for changes to take effect

#### Azure App Service Deployment with Managed Identity

When deploying to Azure App Service, you can use managed identity for secure authentication:

1. Enable system-assigned managed identity on your App Service:
   ```bash
   az webapp identity assign --name <app-name> --resource-group <resource-group>
   ```

2. Grant the identity access to your Azure OpenAI resource:
   ```bash
   # Get the principal ID
   principalId=$(az webapp identity show --name <app-name> --resource-group <resource-group> --query principalId -o tsv)
   
   # Assign the "Cognitive Services OpenAI User" role
   az role assignment create \
     --assignee $principalId \
     --role "Cognitive Services OpenAI User" \
     --scope /subscriptions/<subscription-id>/resourceGroups/<resource-group>/providers/Microsoft.CognitiveServices/accounts/<openai-resource>
   ```

3. Configure App Service settings:
   ```bash
   az webapp config appsettings set --name <app-name> --resource-group <resource-group> --settings \
     AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/ \
     AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name \
     AZURE_OPENAI_API_VERSION=2023-12-01-preview
   ```

#### Switching Between OpenAI and Azure OpenAI

The application automatically detects which API to use based on the available configuration:
- If `AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_DEPLOYMENT_NAME` are defined, Azure OpenAI will be used
- Otherwise, the application will use standard OpenAI with `OPENAI_API_KEY`

This approach allows you to deploy the same application to different environments with different authentication mechanisms.

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

## Containerization & Deployment

### Building the Docker Container

The application can be containerized for consistent deployment. Build the Docker image with:

```bash
# Build for x86_64 architecture (required for Azure App Service)
docker build --platform linux/amd64 -t ai-content-creator:latest .
```

> **Important**: Always use `--platform=linux/amd64` when building on ARM-based machines (like Apple Silicon Macs) to ensure compatibility with Azure App Service, which runs on x86_64 architecture.

### Running Locally with Docker

#### Using Standard OpenAI API:
```bash
docker run -p 8000:80 \
  -e OPENAI_API_KEY="your-api-key" \
  -e OPENAI_DEFAULT_MODEL="gpt-4" \
  -e MAX_TOKENS="4000" \
  -e TEMPERATURE="0.7" \
  ai-content-creator:latest
```

#### Using Azure OpenAI with Your Azure Credentials:
```bash
docker run -p 8000:80 \
  -e AZURE_OPENAI_ENDPOINT="https://your-resource-name.openai.azure.com/" \
  -e AZURE_OPENAI_DEPLOYMENT_NAME="deployment_name" \
  -e AZURE_OPENAI_API_VERSION="2023-12-01-preview" \
  -e OPENAI_DEFAULT_MODEL="gpt-4" \
  -e MAX_TOKENS="4000" \
  -e TEMPERATURE="0.7" \
  -e OPENAI_API_KEY="" \
  -v "$HOME/.azure:/home/appuser/.azure:ro" \
  ai-content-creator:latest
```

Access the application at http://localhost:8000 - including the documentation at http://localhost:8000/docs

### Environment Variables

| Environment Variable | Description | Example Value |
|---------------------|-------------|---------------|
| OPENAI_API_KEY | OpenAI API key (set empty to use Azure OpenAI) | sk-... |
| OPENAI_DEFAULT_MODEL | Model to use for generation | gpt-4 |
| MAX_TOKENS | Maximum tokens for response generation | 4000 |
| TEMPERATURE | Randomness of generation (0.0-1.0) | 0.7 |
| AZURE_OPENAI_ENDPOINT | Azure OpenAI endpoint URL | https://resource.openai.azure.com/ |
| AZURE_OPENAI_DEPLOYMENT_NAME | Azure OpenAI deployment name | gpt4 |
| AZURE_OPENAI_API_VERSION | Azure OpenAI API version | 2023-12-01-preview |
| PORT | Port the application listens on | 80 |
| HOST | Host to bind to | 0.0.0.0 |
| ENVIRONMENT | Environment mode (development/production) | production |
| LOG_LEVEL | Logging level | info |
| PYTHONUNBUFFERED | Ensures logs appear immediately | 1 |
| WEBSITES_PORT | Port for Azure App Service | 80 |

### Deploying to Azure App Service

#### 1. Push to Azure Container Registry (ACR)

```bash
# Login to Azure
az login

# Create ACR if needed
az acr create --resource-group your-resource-group --name yourregistryname --sku Basic

# Login to ACR
az acr login --name yourregistryname

# Build with the correct platform
docker build --platform linux/amd64 -t ai-content-creator:latest .

# Tag and push your image
ACR_LOGINSERVER=$(az acr show --name yourregistryname --query loginServer --output tsv)
docker tag ai-content-creator:latest $ACR_LOGINSERVER/ai-content-creator:latest
docker push $ACR_LOGINSERVER/ai-content-creator:latest
```

#### 2. Create App Service Plan & Web App

```bash
# Create App Service Plan
az appservice plan create \
  --name your-plan-name \
  --resource-group your-resource-group \
  --location eastus \
  --is-linux \
  --sku B1

# Create Web App with container image
az webapp create \
  --resource-group your-resource-group \
  --plan your-plan-name \
  --name your-app-name \
  --deployment-container-image-name "$ACR_LOGINSERVER/ai-content-creator:latest"

# Configure ACR access
az webapp config container set \
  --name your-app-name \
  --resource-group your-resource-group \
  --docker-registry-server-url "https://$ACR_LOGINSERVER" \
  --docker-registry-server-user yourregistryname \
  --docker-registry-server-password $(az acr credential show --name yourregistryname --query "passwords[0].value" --output tsv)
```

#### 3. Configure App Service Settings

```bash
# Essential configuration for container
az webapp config appsettings set \
  --name your-app-name \
  --resource-group your-resource-group \
  --settings \
  WEBSITES_PORT=80 \
  WEBSITE_WARMUP_PATH="/robots933456.txt" \
  WEBSITE_WARMUP_STATUSES="200" \
  LOG_LEVEL="info" \
  PYTHONUNBUFFERED="1"
```

> **Note**: The application implements the `/robots933456.txt` endpoint specifically for Azure App Service's warmup process, which checks container readiness.

#### 4a. Configure for OpenAI API

```bash
az webapp config appsettings set \
  --name your-app-name \
  --resource-group your-resource-group \
  --settings \
  OPENAI_API_KEY="your-openai-api-key" \
  OPENAI_DEFAULT_MODEL="gpt-4" \
  MAX_TOKENS="4000" \
  TEMPERATURE="0.7" \
  AZURE_OPENAI_ENDPOINT="" \
  AZURE_OPENAI_DEPLOYMENT_NAME=""
```

#### 4b. Configure for Azure OpenAI with Managed Identity

```bash
# Enable system-assigned managed identity
az webapp identity assign \
  --name your-app-name \
  --resource-group your-resource-group

# Get the principal ID
PRINCIPAL_ID=$(az webapp identity show \
  --name your-app-name \
  --resource-group your-resource-group \
  --query principalId -o tsv)

# Get Azure OpenAI resource ID
OPENAI_NAME="your-openai-resource"
OPENAI_ID=$(az cognitiveservices account show \
  --name $OPENAI_NAME \
  --resource-group your-resource-group \
  --query id -o tsv)

# Grant the managed identity "Cognitive Services OpenAI User" role
az role assignment create \
  --assignee $PRINCIPAL_ID \
  --role "Cognitive Services OpenAI User" \
  --scope $OPENAI_ID

# Update settings for Azure OpenAI
az webapp config appsettings set \
  --name your-app-name \
  --resource-group your-resource-group \
  --settings \
  OPENAI_API_KEY="" \
  AZURE_OPENAI_ENDPOINT="https://$OPENAI_NAME.openai.azure.com/" \
  AZURE_OPENAI_DEPLOYMENT_NAME="your-deployment-name" \
  AZURE_OPENAI_API_VERSION="2023-12-01-preview" \
  OPENAI_DEFAULT_MODEL="gpt-4" \
  MAX_TOKENS="4000" \
  TEMPERATURE="0.7"
```

#### 5. Restart and Access Your App

```bash
# Restart the app to apply configuration
az webapp restart --name your-app-name --resource-group your-resource-group

# Get the app URL
APP_URL=$(az webapp show --name your-app-name --resource-group your-resource-group --query defaultHostName -o tsv)
echo "App URL: https://$APP_URL"
```

Access your application at `https://your-app-name.azurewebsites.net`

### Troubleshooting

If encountering issues:

1. Check container logs:
   ```bash
   az webapp log tail --name your-app-name --resource-group your-resource-group
   ```

2. Verify the container is running:
   ```bash
   az webapp config container show --name your-app-name --resource-group your-resource-group
   ```

3. Common issues:
   - **Architecture Mismatch**: Ensure you build with `--platform=linux/amd64` 
   - **Port Configuration**: Verify `WEBSITES_PORT=80` is set
   - **Warmup Failures**: Check `/robots933456.txt` endpoint returns 200
   - **Authentication Issues**: Ensure Managed Identity has the proper role assignment
   - **Container Access**: Verify ACR credentials are correctly configured

4. Check the health endpoint:
   ```bash
   curl -X GET https://your-app-name.azurewebsites.net/health
   ```
