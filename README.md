# AI Content Creator

A FastAPI backend for processing documents, generating customer intent statements, suggesting content types, and creating AI-powered content based on document input.

## Table of Contents

- [Overview](#overview)
- [For API Consumers](#for-api-consumers)
  - [API Endpoints](#api-endpoints)
  - [Using the Customer Intent Endpoint](#using-the-customer-intent-endpoint)
  - [Using the Content Types Endpoint](#using-the-content-types-endpoint)
  - [Using the Content Generate Endpoint](#using-the-content-generate-endpoint)
  - [API Response Formats](#api-response-formats)
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

This application provides a complete AI content creation workflow. It processes document files (.docx, .md, .txt), extracts text, and uses OpenAI's models to:

1. Generate customer intent statements in the format: "As a [user type], I want to [action] because [reason]"
2. Recommend appropriate content types based on the Diátaxis framework (Tutorials, How-To Guides, Explanations, Reference)
3. Generate complete, structured content for each selected content type

The application handles file upload, text extraction, token validation, and AI content generation in a seamless workflow.

---

## For API Consumers

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information with available endpoints |
| GET | `/health` | Health check endpoint for monitoring |
| POST | `/api/v1/customer-intent` | Generate customer intent from document |
| POST | `/api/v1/content-types` | Recommend content types based on customer intent and text |
| POST | `/api/v1/content-generate` | Generate detailed content for selected content types |

### Using the Customer Intent Endpoint

Send a POST request to `/api/v1/customer-intent` with a file in the request body:
- Content-Type: `multipart/form-data`
- Form field name: `file`
- Supported file types: `.docx`, `.md`, `.txt`

### Using the Content Types Endpoint

Send a POST request to `/api/v1/content-types` with a JSON body:
```json
{
  "intent": "As a marketing manager, I want to create engaging content about our new product because I need to increase customer awareness",
  "text_used": "Text content extracted from the document..."
}
```

### Using the Content Generate Endpoint

Send a POST request to `/api/v1/content-generate` with a JSON body:
```json
{
  "intent": "As a marketing manager, I want to create engaging content about our new product because I need to increase customer awareness",
  "text_used": "Text content extracted from the document...",
  "content_types": [
    {
      "type": "tutorial",
      "title": "Getting Started with Our New Product"
    },
    {
      "type": "how-to",
      "title": "How to Maximize Results with Our New Product"
    }
  ]
}
```

### API Response Formats

**Customer Intent Response (200 OK):**
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

**Content Types Response (200 OK):**
```json
{
  "selected_types": [
    {
      "type": "tutorial",
      "confidence": 0.9,
      "reasoning": "The content is well-suited for a tutorial because it involves a step-by-step learning process..."
    },
    {
      "type": "how-to",
      "confidence": 0.8,
      "reasoning": "The content contains practical problem-solving steps that would work well as a how-to guide..."
    }
  ],
  "model": "gpt-4",
  "model_family": "gpt",
  "capabilities": {
    "supports_functions": true,
    "supports_vision": false,
    "supports_embeddings": true
  },
  "usage": {
    "prompt_tokens": 456,
    "completion_tokens": 78,
    "total_tokens": 534
  },
  "token_limit": 8192,
  "token_count": 1500,
  "remaining_tokens": 6692,
  "text_used": "Text content used for content type selection..."
}
```

**Content Generate Response (200 OK):**
```json
{
  "generated_content": [
    {
      "type": "tutorial",
      "title": "Getting Started with Our New Product",
      "content": "# Getting Started with Our New Product\n\n## Introduction\nThis tutorial will guide you through..."
    },
    {
      "type": "how-to",
      "title": "How to Maximize Results with Our New Product",
      "content": "# How to Maximize Results with Our New Product\n\n## Overview\nThis guide explains how to..."
    }
  ],
  "model": "gpt-4",
  "model_family": "gpt",
  "capabilities": {
    "supports_functions": true,
    "supports_vision": false,
    "supports_embeddings": true
  },
  "usage": {
    "prompt_tokens": 789,
    "completion_tokens": 1234,
    "total_tokens": 2023
  },
  "token_limit": 8192,
  "token_count": 3000,
  "remaining_tokens": 5192,
  "text_used": "Text content used for content generation..."
}
```

### Error Handling

| Status Code | Description | Resolution |
|-------------|-------------|------------|
| 400 | Bad Request - Invalid input | Check file format, content, or request body |
| 413 | Request Entity Too Large | Document exceeds token limit, use shorter document |
| 415 | Unsupported Media Type | Use a supported file type (.docx, .md, .txt) |
| 500 | Internal Server Error | Server issue, retry later |

### Using cURL

#### Customer Intent Endpoint:

```bash
curl -X POST \
  -F "file=@/path/to/your/document.docx" \
  http://localhost:8000/api/v1/customer-intent
```

#### Content Types Endpoint:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "intent": "As a marketing manager, I want to create engaging content about our new product because I need to increase customer awareness",
    "text_used": "Your document text here..."
  }' \
  http://localhost:8000/api/v1/content-types
```

#### Content Generate Endpoint:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "intent": "As a marketing manager, I want to create engaging content about our new product because I need to increase customer awareness",
    "text_used": "Your document text here...",
    "content_types": [
      {
        "type": "tutorial",
        "title": "Getting Started with Our New Product"
      },
      {
        "type": "how-to",
        "title": "How to Maximize Results with Our New Product"
      }
    ]
  }' \
  http://localhost:8000/api/v1/content-generate
```

### Python Client Example

```python
import requests
import json

def generate_content_workflow(file_path, api_url):
    """
    Complete content generation workflow using the API
    
    Args:
        file_path: Path to the document file (.docx, .md, or .txt)
        api_url: Base URL of the deployed API
    
    Returns:
        Generated content for each content type
    """
    # Step 1: Generate customer intent
    intent_endpoint = f"{api_url}/api/v1/customer-intent"
    
    # Open the file in binary mode
    with open(file_path, 'rb') as file:
        # Create the files dictionary for multipart/form-data upload
        files = {
            'file': (file.name, file, 'application/octet-stream')
        }
        
        # Make the POST request
        intent_response = requests.post(intent_endpoint, files=files)
    
    # Check for errors
    intent_response.raise_for_status()
    intent_data = intent_response.json()
    
    print(f"Generated Intent: {intent_data['intent']}")
    
    # Step 2: Get content type recommendations
    content_types_endpoint = f"{api_url}/api/v1/content-types"
    content_types_request = {
        "intent": intent_data["intent"],
        "text_used": intent_data["text_used"]
    }
    
    content_types_response = requests.post(
        content_types_endpoint, 
        json=content_types_request
    )
    
    # Check for errors
    content_types_response.raise_for_status()
    content_types_data = content_types_response.json()
    
    print(f"Recommended content types:")
    for content_type in content_types_data["selected_types"]:
        print(f"- {content_type['type']} (confidence: {content_type['confidence']})")
    
    # Step 3: Generate content for selected types
    content_generate_endpoint = f"{api_url}/api/v1/content-generate"
    
    # Prepare content types request - choose types with confidence > 0.5
    selected_types = [
        {"type": ct["type"]}
        for ct in content_types_data["selected_types"]
        if ct["confidence"] > 0.5
    ]
    
    content_generate_request = {
        "intent": intent_data["intent"],
        "text_used": intent_data["text_used"],
        "content_types": selected_types
    }
    
    content_generate_response = requests.post(
        content_generate_endpoint,
        json=content_generate_request
    )
    
    # Check for errors
    content_generate_response.raise_for_status()
    content_generate_data = content_generate_response.json()
    
    # Return the generated content
    return content_generate_data

# Example usage
if __name__ == "__main__":
    # Replace with your API URL
    api_url = "http://localhost:8000"
    
    # File to upload
    document_path = "path/to/document.docx"
    
    try:
        # Call the complete workflow
        result = generate_content_workflow(document_path, api_url)
        
        # Print the titles of generated content
        print("\nGenerated content:")
        for content in result["generated_content"]:
            print(f"- {content['type']}: {content['title']}")
            
        # Save the content to files
        for content in result["generated_content"]:
            filename = f"{content['type']}_{content['title'].replace(' ', '_')}.md"
            with open(filename, 'w') as f:
                f.write(content['content'])
            print(f"Saved {filename}")
        
    except requests.exceptions.HTTPError as e:
        print(f"API request failed: {e}")
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
│   │   ├── customer_intent/
│   │   │   ├── models/
│   │   │   │   └── ai_customer_intent_model.py # Request/response models
│   │   │   ├── routers/
│   │   │   │   └── ai_customer_intent_router.py # Customer intent endpoint
│   │   │   ├── services/
│   │   │   │   └── ai_customer_intent_service.py # Intent prompt structure
│   │   ├── content_types/
│   │   │   ├── models/
│   │   │   │   ├── content_type_model.py # Content type models
│   │   │   │   └── content_types_config.py # Diátaxis framework definitions
│   │   │   ├── routers/
│   │   │   │   └── content_type_router.py # Content type endpoint
│   │   │   ├── services/
│   │   │   │   └── content_type_service.py # Content type prompt structure
│   │   ├── content_generate/
│   │   │   ├── models/
│   │   │   │   └── content_generate_model.py # Content generation models
│   │   │   ├── routers/
│   │   │   │   └── content_generate_router.py # Content generation endpoint
│   │   │   ├── services/
│   │   │   │   └── content_generate_service.py # Content generation logic
│   ├── shared/
│   │   └── logging.py                   # Logging configuration
│   ├── main.py                          # Application entry point
├── tests/                               # Test suite
├── server.py                            # Server startup
├── requirements.txt                     # Dependencies
└── .env-example                         # Environment template
```

### Execution Flow

The application supports a complete content creation workflow:

1. **Customer Intent Generation**:
   - User uploads a document to `/api/v1/customer-intent`
   - File processing detects format and extracts text
   - AI service generates a structured customer intent statement

2. **Content Type Selection**:
   - User sends intent and text to `/api/v1/content-types`
   - AI analyzes content needs and recommends appropriate Diátaxis content types
   - Service returns selected types with confidence scores and reasoning

3. **Content Generation**:
   - User sends intent, text, and selected content types to `/api/v1/content-generate`
   - For each content type, AI generates complete structured content
   - Service returns all generated content in markdown format

Each step involves:
1. **Token counting and validation** using `tokenizer_core_service.py`
2. **Prompt formatting** using the corresponding service for that feature
3. **AI processing** using the shared `ai_core_service.py`
4. **Response formatting** in standardized JSON structure with metadata

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
