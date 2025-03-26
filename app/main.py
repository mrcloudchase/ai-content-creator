from fastapi import FastAPI
from app.routers import documents

app = FastAPI(
    title="Document Parser API",
    description="API for parsing .docx documents and maintaining their structure",
    version="0.1.0"
)

# API versioning prefix
API_V1_PREFIX = "/api/v1"

# Apply version prefix to document routes
app.include_router(
    documents.router,
    prefix=API_V1_PREFIX
)

@app.get("/")
async def root():
    return {
        "name": "Document Parser API",
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