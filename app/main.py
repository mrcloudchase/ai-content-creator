from fastapi import FastAPI, Request
from app.ai.customer_intent.routers.ai_customer_intent_router import router as customer_intent_router
from app.shared.logging import setup_app_logging, LoggingMiddleware, app_logger
import os
import datetime

# Set up application logging
logger = setup_app_logging()
logger.info("Starting AI Content Developer API")

app = FastAPI(
    title="AI Content Developer API",
    description="API application for generating AI content",
    version="0.4.0"
)

# Add logging middleware
app.add_middleware(LoggingMiddleware)

# API versioning prefix
API_V1_PREFIX = "/api/v1"

# Include the Customer Intent router with proper prefix
app.include_router(
    customer_intent_router,
    prefix=API_V1_PREFIX
)

# Azure App Service warmup endpoint
@app.get("/robots933456.txt")
async def warmup():
    """
    Default warmup path for Azure App Service.
    Used by the platform to determine when the container is ready.
    """
    return "Warmup request handled successfully"

@app.get("/")
async def root(request: Request):
    # Use the request-specific logger if available
    logger = getattr(request.state, "logger", app_logger)
    logger.info("Root endpoint accessed")
    
    return {
        "name": "AI Content Developer API",
        "version": app.version,
        "documentation": "/docs",
        "endpoints": {
            "health": "/health",
            "api_base": API_V1_PREFIX,
            "customer_intent": f"{API_V1_PREFIX}/customer-intent - Upload a document to generate customer intent statement"
        }
    }

@app.get("/health", status_code=200)
async def health_check(request: Request):
    """
    Health check endpoint to verify the service is running
    Azure App Service uses this to determine container health
    
    Returns:
        Dict: Status information about the service
    """
    # Use the request-specific logger if available
    logger = getattr(request.state, "logger", app_logger)
    logger.debug("Health check endpoint accessed")
    
    # Add more information that's useful for monitoring
    return {
        "status": "healthy",
        "service": "ai-content-developer-api",
        "version": app.version,
        "environment": os.getenv("ENVIRONMENT", "production"),
        "site_name": os.getenv("WEBSITE_SITE_NAME", "local"),
        "server_time": datetime.datetime.now().isoformat()
    } 