from pydantic_settings import BaseSettings
from pydantic import field_validator
import os
from typing import Optional

class LoggingSettings(BaseSettings):
    """Settings for logging configuration"""
    
    # Log level (debug, info, warning, error, critical)
    LOG_LEVEL: str = "info"
    
    # Whether to log to console
    LOG_TO_CONSOLE: bool = True
    
    # Whether to log to file
    LOG_TO_FILE: bool = False
    
    # Directory where log files are stored
    LOG_DIR: Optional[str] = None
    
    # Name of the log file
    LOG_FILE_NAME: str = "ai_content_developer.log"
    
    # Max size of log file before rotation (in MB)
    MAX_LOG_FILE_SIZE_MB: int = 5
    
    # Number of backup log files to keep
    BACKUP_COUNT: int = 3
    
    @field_validator('LOG_LEVEL')
    @classmethod
    def validate_log_level(cls, v):
        valid_levels = ['debug', 'info', 'warning', 'error', 'critical']
        if v.lower() not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}")
        return v.lower()
    
    @property
    def log_file_path(self) -> Optional[str]:
        """Get the full path to the log file"""
        if not self.LOG_TO_FILE or not self.LOG_DIR:
            return None
        
        return os.path.join(self.LOG_DIR, self.LOG_FILE_NAME)
    
    class Config:
        env_prefix = "APP_LOGGING_"
        case_sensitive = True 