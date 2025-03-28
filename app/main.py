from fastapi import FastAPI
from app.routers import documents, ai, tokens
from app.routers import customer_intent
from app.routers import markdown

app = FastAPI(
    title="Document Parser & AI API",
    description="API for parsing .docx documents and generating AI completions",
    version="0.3.0"
)

# API versioning prefix
API_V1_PREFIX = "/api/v1"

# Apply version prefix to routes
app.include_router(
    documents.router,
    prefix=API_V1_PREFIX
)

# Include the AI router
app.include_router(
    ai.router,
    prefix=API_V1_PREFIX
)

# Include the new Tokens router
app.include_router(
    tokens.router,
    prefix=API_V1_PREFIX
)

# Include the Customer Intent router
app.include_router(
    customer_intent.router,
    prefix=API_V1_PREFIX
)

# Include the Markdown router
app.include_router(
    markdown.router,
    prefix=API_V1_PREFIX
)

@app.get("/")
async def root():
    return {
        "name": "Document Parser & AI API",
        "version": app.version,
        "documentation": "/docs",
        "endpoints": {
            "health": "/health",
            "api_base": API_V1_PREFIX
        }
    }

@app.get("/health", status_code=200)
async def health_check():
    """
    Health check endpoint to verify the service is running
    
    Returns:
        Dict: Status information about the service
    """
    return {
        "status": "healthy",
        "service": "document-parser-api",
        "version": app.version
    } 