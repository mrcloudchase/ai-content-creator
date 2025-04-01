import uvicorn
import os
import sys

if __name__ == "__main__":
    # Get configuration from environment variables
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8080"))
    
    # Determine if in development or production
    # In Azure App Service / Docker, we don't want auto-reload
    is_dev = os.getenv("ENVIRONMENT", "production").lower() == "development"
    
    # Print configuration for diagnostics
    print(f"Starting server on {host}:{port}, environment={os.getenv('ENVIRONMENT', 'production')}")
    print(f"App Service info: site={os.getenv('WEBSITE_SITE_NAME', 'local')}, hostname={os.getenv('WEBSITE_HOSTNAME', 'localhost')}")
    
    # Configure logging 
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    
    try:
        # Start the server
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            reload=is_dev,
            log_level=log_level
        )
    except Exception as e:
        print(f"Failed to start server: {str(e)}", file=sys.stderr)
        sys.exit(1) 