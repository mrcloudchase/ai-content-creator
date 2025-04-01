from .logger import Logger, app_logger
from .middleware import LoggingMiddleware
from .config import LoggingSettings

# Initialize settings
logging_settings = LoggingSettings()

# Configure global logging settings first
Logger.configure_global_settings(
    log_to_file=logging_settings.LOG_TO_FILE,
    log_file_path=logging_settings.log_file_path,
    max_log_file_size=logging_settings.MAX_LOG_FILE_SIZE_MB * 1024 * 1024,
    backup_count=logging_settings.BACKUP_COUNT
)

# Create a function to set up application-wide logging
def setup_app_logging():
    """Set up application-wide logging based on settings"""
    return Logger.setup_logger(
        logger_name="ai_content_developer",
        log_level=logging_settings.LOG_LEVEL,
        log_to_console=logging_settings.LOG_TO_CONSOLE
        # No need to pass file settings again as they're already configured globally
    )

# Export convenience functions and objects
get_logger = Logger.get_logger
get_request_logger = Logger.get_request_logger
