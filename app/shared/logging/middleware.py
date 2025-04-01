import time
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from .logger import Logger

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging requests and responses with timing information"""
    
    async def dispatch(self, request: Request, call_next):
        # Generate a unique request ID
        request_id = str(uuid.uuid4())
        
        # Create a request-specific logger
        logger = Logger.get_request_logger(request_id)
        
        # Attach the logger to the request state for access in endpoints
        request.state.logger = logger
        
        # Log the start of the request
        start_time = time.time()
        logger.info(f"Request started: {request.method} {request.url.path}")
        
        # Process the request
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log the end of the request
            logger.info(
                f"Request completed: {request.method} {request.url.path} - "
                f"Status: {response.status_code} - "
                f"Duration: {process_time:.4f}s"
            )
            
            # Add request ID to response headers for tracing
            response.headers["X-Request-ID"] = request_id
            
            return response
        except Exception as e:
            # Log any unhandled exceptions
            process_time = time.time() - start_time
            logger.error(
                f"Request failed: {request.method} {request.url.path} - "
                f"Duration: {process_time:.4f}s - "
                f"Error: {str(e)}"
            )
            raise  # Re-raise the exception for FastAPI's exception handlers 