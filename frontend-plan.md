# AI Content Creator Frontend

This document outlines the plan for creating a modern, minimalist frontend for the AI Content Creator service using Python and Streamlit.

## Overview

The frontend will be a containerized application that interacts with the existing AI Content Creator API, following the complete workflow:

1. **File Upload**: Allow users to upload documents (.docx, .md, .txt)
2. **Customer Intent Generation**: Display generated intent statement
3. **Content Type Selection**: Show recommended content types with confidence scores
4. **Content Generation**: Generate and display content for selected types

## Technology Stack

- **Framework**: Streamlit (Python-based web app framework)
- **HTTP Client**: requests (for API communication)
- **Styling**: Custom CSS for minimalist design
- **Containerization**: Docker
- **Deployment**: Compatible with the existing API service container

## Project Structure

```
frontend/
├── app/
│   ├── main.py                  # Main Streamlit application
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── api_client.py        # Client for API communication
│   │   └── content_display.py   # Utilities for displaying content
│   ├── components/
│   │   ├── __init__.py
│   │   ├── file_upload.py       # File upload component
│   │   ├── intent_display.py    # Intent display component
│   │   ├── content_type_selector.py  # Content type selection
│   │   └── content_viewer.py    # Content viewing component
│   └── assets/
│       ├── styles.css           # Custom CSS styles
│       └── logo.png             # Application logo
├── Dockerfile                   # Container configuration
├── requirements.txt             # Dependencies
├── .streamlit/
│   └── config.toml              # Streamlit configuration
└── README.md                    # Frontend documentation
```

## Implementation Plan

### 1. API Client Module

Create a client module to handle communication with the backend API:

```python
# api_client.py
class ContentCreatorClient:
    def __init__(self, base_url):
        self.base_url = base_url
        
    def generate_intent(self, file):
        # POST to /api/v1/customer-intent
        
    def get_content_types(self, intent, text_used):
        # POST to /api/v1/content-types
        
    def generate_content(self, intent, text_used, content_types):
        # POST to /api/v1/content-generate
```

### 2. Main Application Flow

The main Streamlit application will implement a wizard-like flow:

```python
# main.py
import streamlit as st
from utils.api_client import ContentCreatorClient
from components.file_upload import render_file_upload
from components.intent_display import render_intent
from components.content_type_selector import render_content_types
from components.content_viewer import render_content

# Initialize session state
if 'step' not in st.session_state:
    st.session_state.step = 'upload'

# Initialize API client
api_client = ContentCreatorClient(base_url=st.secrets["api_url"])

# Application header
st.title("AI Content Creator")

# Multi-step workflow
if st.session_state.step == 'upload':
    render_file_upload()
    
elif st.session_state.step == 'intent':
    render_intent(st.session_state.intent_data)
    
elif st.session_state.step == 'content_types':
    render_content_types(st.session_state.content_types_data)
    
elif st.session_state.step == 'content':
    render_content(st.session_state.generated_content)
```

### 3. Component Implementation

Each component will be implemented in a separate module:

**File Upload Component**
```python
# file_upload.py
def render_file_upload():
    st.subheader("Upload a Document")
    uploaded_file = st.file_uploader("Choose a file", type=['docx', 'md', 'txt'])
    
    if uploaded_file and st.button("Generate Intent"):
        with st.spinner("Generating customer intent..."):
            response = api_client.generate_intent(uploaded_file)
            st.session_state.intent_data = response
            st.session_state.step = 'intent'
            st.rerun()
```

**Intent Display Component**
```python
# intent_display.py
def render_intent(intent_data):
    st.subheader("Customer Intent")
    st.info(intent_data["intent"])
    
    # Display model info, token usage, etc.
    
    if st.button("Suggest Content Types"):
        with st.spinner("Analyzing content types..."):
            response = api_client.get_content_types(
                intent_data["intent"], 
                intent_data["text_used"]
            )
            st.session_state.content_types_data = response
            st.session_state.step = 'content_types'
            st.rerun()
            
    if st.button("Back"):
        st.session_state.step = 'upload'
        st.rerun()
```

**Content Type Selector Component**
```python
# content_type_selector.py
def render_content_types(content_types_data):
    st.subheader("Recommended Content Types")
    
    selected_types = []
    for content_type in content_types_data["selected_types"]:
        col1, col2 = st.columns([1, 4])
        with col1:
            selected = st.checkbox("", value=content_type["confidence"] > 0.7)
        with col2:
            st.write(f"**{content_type['type'].title()}** (Confidence: {content_type['confidence']:.2f})")
            st.write(content_type["reasoning"])
            
        if selected:
            selected_types.append({"type": content_type["type"]})
    
    if selected_types and st.button("Generate Content"):
        with st.spinner("Generating content..."):
            response = api_client.generate_content(
                content_types_data["intent"],
                content_types_data["text_used"],
                selected_types
            )
            st.session_state.generated_content = response
            st.session_state.step = 'content'
            st.rerun()
            
    if st.button("Back"):
        st.session_state.step = 'intent'
        st.rerun()
```

**Content Viewer Component**
```python
# content_viewer.py
def render_content(content_data):
    st.subheader("Generated Content")
    
    # Create tabs for each content type
    tabs = st.tabs([content["type"].title() for content in content_data["generated_content"]])
    
    for i, tab in enumerate(tabs):
        with tab:
            content = content_data["generated_content"][i]
            st.markdown(f"## {content['title']}")
            st.markdown(content["content"])
            
            # Add download button for each content
            st.download_button(
                "Download as Markdown",
                content["content"],
                file_name=f"{content['type']}_{content['title'].replace(' ', '_')}.md",
                mime="text/markdown"
            )
    
    # Display model info and token usage
    with st.expander("Generation Details"):
        st.json({"model": content_data["model"], "usage": content_data["usage"]})
            
    if st.button("Start Over"):
        st.session_state.step = 'upload'
        # Clear session data
        for key in ['intent_data', 'content_types_data', 'generated_content']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
```

### 4. UI Design Principles

To achieve a modern, minimalist design:

1. **Clean Interface**: Focus on content with ample whitespace
2. **Progressive Disclosure**: Only show relevant controls at each step
3. **Consistent Visual Hierarchy**: Clear headings and status indicators
4. **Custom CSS**: Use custom styles for a refined look
5. **Responsive Layout**: Adapt to different screen sizes
6. **Loading States**: Show spinners during API calls
7. **Error Handling**: Graceful error displays with actionable messages

### 5. Containerization

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### 6. Configuration

The Streamlit configuration will be stored in `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#5D87E1"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
enableCORS = false
enableXsrfProtection = true
```

### 7. Deployment Strategy

The frontend will be deployed as a container that communicates with the API service container:

1. **Docker Compose**: For local development and testing
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
   ```

2. **Kubernetes**: For production deployment
   - Deploy both containers in the same pod or with service networking
   - Use config maps for environment variables
   - Use secrets for API credentials

### 8. Development Workflow

1. **Setup API Client**: Create and test API communication
2. **Implement Components**: Build each UI component
3. **Integrate Flow**: Connect components in the main application
4. **Style & Polish**: Apply custom CSS and refine UX
5. **Containerize**: Package the application
6. **Test End-to-End**: Validate the complete workflow
7. **Document**: Create usage documentation

### 9. Future Enhancements

Potential enhancements for future versions:

1. **Content Editing**: Allow users to edit generated content
2. **Project Management**: Save and manage multiple content generation projects
3. **Export Options**: Additional export formats (PDF, HTML, etc.)
4. **Preview Modes**: Visual previews of how content would look when published
5. **Progress Tracking**: Visualize token usage and generation progress
6. **Content Templates**: Pre-defined templates for different types of content

## Conclusion

This plan outlines a modern, minimalist frontend for the AI Content Creator service using Streamlit. The implementation focuses on a clean, step-by-step user experience that guides users through the content creation workflow, from document upload to final content generation. The containerized approach allows for easy deployment alongside the API service container. 