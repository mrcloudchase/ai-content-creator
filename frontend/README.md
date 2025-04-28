# AI Content Creator Frontend

A modern, minimalist frontend for the AI Content Creator service built with Streamlit.

## Overview

This application provides a user-friendly interface for the AI Content Creator API, following a complete content creation workflow:

1. **Document Upload**: Upload documents in .docx, .md, or .txt format
2. **Customer Intent Generation**: Automatically extract customer intent from the document
3. **Content Type Selection**: Choose recommended content types based on the customer intent
4. **Content Generation**: Generate complete, structured content for each selected type

## Features

- Clean, intuitive user interface
- Step-by-step wizard flow
- Document upload and processing
- Content previews with syntax highlighting
- Markdown export functionality
- Responsive design for desktop and mobile

## Requirements

- Python 3.12+
- Streamlit 1.32.0+
- Requests 2.31.0+
- Connection to AI Content Creator API

## Quick Start

### Local Development

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd ai-content-creator/frontend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set the API URL environment variable:
   ```bash
   # Linux/Mac
   export API_URL=http://localhost:8000
   
   # Windows
   set API_URL=http://localhost:8000
   ```

5. Run the application:
   ```bash
   streamlit run app/main.py
   ```

6. Access the application at http://localhost:8501

### Docker Container

1. Build the Docker image:
   ```bash
   docker build -t ai-content-creator-frontend .
   ```

2. Run the container:
   ```bash
   docker run -p 8501:8501 -e API_URL=http://localhost:8000 ai-content-creator-frontend
   ```

3. Access the application at http://localhost:8501

## Running with Docker Compose

For a complete setup with both the API and frontend, use Docker Compose:

```yaml
version: '3'
services:
  api:
    image: ai-content-creator:latest
    ports:
      - "8000:80"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      
  frontend:
    image: ai-content-creator-frontend:latest
    ports:
      - "8501:8501"
    environment:
      - API_URL=http://api:80
    depends_on:
      - api
```

Save this as `docker-compose.yml` and run:

```bash
docker-compose up
```

## Configuration

### Environment Variables

- `API_URL`: URL of the AI Content Creator API (default: http://localhost:8000)

### Streamlit Configuration

The application uses custom theming defined in `.streamlit/config.toml`. You can modify the theme colors and other settings in this file.

## Usage Flow

1. **Upload Document**: 
   - Click "Browse files" to select a document
   - Click "Generate Intent" to process the document

2. **Review Customer Intent**:
   - Review the generated customer intent statement
   - Click "Suggest Content Types" to continue

3. **Select Content Types**:
   - Select the content types you want to generate
   - Click "Generate Content" to proceed

4. **View and Download Content**:
   - View the generated content for each type
   - Use the download buttons to save content as Markdown files

## Troubleshooting

- **API Connection Issues**: Verify that the API service is running and accessible at the configured URL
- **Upload Errors**: Ensure the document is in a supported format (.docx, .md, .txt) and under 10MB
- **Content Generation Errors**: Check that the OpenAI API key is properly configured in the API service

## License

[MIT License](LICENSE) 