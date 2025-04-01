import logging
import sys
import os
from logging.handlers import RotatingFileHandler
from typing import Optional

# Default log format
DEFAULT_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DEFAULT_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Log levels
LOG_LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}

class Logger:
    """
    Unified logging interface for the application.
    Provides consistent log formatting and behavior across the app.
    """
    
    # Class-level settings to store global logging configuration
    _config = {
        'log_to_file': False,
        'log_file_path': None,
        'max_log_file_size': 5 * 1024 * 1024,
        'backup_count': 3
    }
    
    @classmethod
    def configure_global_settings(cls, 
                                log_to_file: bool = False,
                                log_file_path: Optional[str] = None,
                                max_log_file_size: int = 5 * 1024 * 1024,
                                backup_count: int = 3):
        """
        Configure global logging settings that apply to all loggers
        """
        cls._config['log_to_file'] = log_to_file
        cls._config['log_file_path'] = log_file_path
        cls._config['max_log_file_size'] = max_log_file_size
        cls._config['backup_count'] = backup_count
    
    @staticmethod
    def setup_logger(
        logger_name: str,
        log_level: str = 'info',
        log_format: Optional[str] = None,
        date_format: Optional[str] = None,
        log_to_console: bool = True,
        log_to_file: Optional[bool] = None,
        log_file_path: Optional[str] = None,
        max_log_file_size: Optional[int] = None,
        backup_count: Optional[int] = None
    ) -> logging.Logger:
        """
        Set up a logger with consistent formatting and handlers.
        
        Args:
            logger_name: Name of the logger
            log_level: Log level (debug, info, warning, error, critical)
            log_format: Format for log messages
            date_format: Format for dates in log messages
            log_to_console: Whether to log to console
            log_to_file: Whether to log to file (overrides global setting if provided)
            log_file_path: Path to log file (overrides global setting if provided)
            max_log_file_size: Maximum size of log file before rotation (overrides global setting if provided)
            backup_count: Number of backup log files to keep (overrides global setting if provided)
            
        Returns:
            Configured logger instance
        """
        # Store configuration for other loggers if provided
        if log_to_file is not None and log_file_path is not None:
            Logger.configure_global_settings(
                log_to_file=log_to_file,
                log_file_path=log_file_path,
                max_log_file_size=max_log_file_size or Logger._config['max_log_file_size'],
                backup_count=backup_count or Logger._config['backup_count']
            )
        else:
            # Use global settings if not explicitly provided
            log_to_file = Logger._config['log_to_file']
            log_file_path = Logger._config['log_file_path']
            max_log_file_size = Logger._config['max_log_file_size']
            backup_count = Logger._config['backup_count']
            
        # Get the log level
        level = LOG_LEVELS.get(log_level.lower(), logging.INFO)
        
        # Create logger
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
        
        # Clear existing handlers to avoid duplicates
        if logger.handlers:
            logger.handlers.clear()
        
        # Set up formatter
        formatter = logging.Formatter(
            log_format or DEFAULT_LOG_FORMAT,
            datefmt=date_format or DEFAULT_DATE_FORMAT
        )
        
        # Console handler
        if log_to_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        # File handler
        if log_to_file and log_file_path:
            try:
                # Ensure directory exists
                os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
                
                # Create rotating file handler
                file_handler = RotatingFileHandler(
                    log_file_path,
                    maxBytes=max_log_file_size,
                    backupCount=backup_count
                )
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
                print(f"Added file handler to logger {logger_name} writing to {log_file_path}")
            except Exception as e:
                # Log error but don't crash
                print(f"Error setting up file logging: {str(e)}")
        
        return logger

    @staticmethod
    def get_logger(name: str, log_level: str = 'info') -> logging.Logger:
        """
        Get a logger with the given name and level.
        
        Args:
            name: Name of the logger
            log_level: Log level (debug, info, warning, error, critical)
            
        Returns:
            Configured logger instance
        """
        # This will use the globally configured file logging settings
        return Logger.setup_logger(name, log_level)
        
    @classmethod
    def get_request_logger(cls, request_id: str) -> logging.Logger:
        """
        Get a logger for request tracking.
        This includes request ID in the log format for traceability.
        
        Args:
            request_id: Unique identifier for the request
            
        Returns:
            Logger configured for request tracking
        """
        request_format = f'%(asctime)s - [RequestID: {request_id}] - %(name)s - %(levelname)s - %(message)s'
        # This will use the globally configured file logging settings
        return cls.setup_logger(f"request.{request_id}", log_format=request_format)

# Default application logger
app_logger = Logger.get_logger("ai_content_developer") 