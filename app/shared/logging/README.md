# Shared Logging Functionality

This module provides a unified logging interface for the AI Content Developer application.

## Features

- Consistent logging format across the application
- Request ID tracking for tracing requests through the system
- Configurable log levels (debug, info, warning, error, critical)
- Console and file logging options
- Rotating file logs with configurable size and backup count
- Middleware for automatic request/response logging

## Usage

### Basic Logging

```python
from app.shared.logging import get_logger

# Get a logger with a specific name
logger = get_logger("my_module")

# Log messages at different levels
logger.debug("Debug information for troubleshooting")
logger.info("Informational message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical error message")
```

### Request-Specific Logging

In endpoint functions that have access to the request object:

```python
@app.get("/some-endpoint")
async def some_endpoint(request: Request):
    # Get the request-specific logger
    logger = getattr(request.state, "logger", fallback_logger)
    
    # Log with request context
    logger.info("Processing request")
    
    # ... endpoint logic ...
    
    return {"result": "success"}
```

### Configuration

Logging is configured through environment variables:

- `APP_LOGGING_LOG_LEVEL`: Log level (debug, info, warning, error, critical)
- `APP_LOGGING_LOG_TO_CONSOLE`: Whether to log to console (true/false)
- `APP_LOGGING_LOG_TO_FILE`: Whether to log to file (true/false)
- `APP_LOGGING_LOG_DIR`: Directory for log files
- `APP_LOGGING_LOG_FILE_NAME`: Name of the log file
- `APP_LOGGING_MAX_LOG_FILE_SIZE_MB`: Max log file size before rotation (in MB)
- `APP_LOGGING_BACKUP_COUNT`: Number of backup log files to keep

## Integration

To integrate the logging middleware with FastAPI:

```python
from fastapi import FastAPI
from app.shared.logging import LoggingMiddleware, setup_app_logging

# Set up application logging
logger = setup_app_logging()

app = FastAPI()

# Add logging middleware
app.add_middleware(LoggingMiddleware)
``` 