from pydantic import field_validator, ConfigDict
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()

class OpenAISettings(BaseSettings):
    """Settings for OpenAI API integration"""
    api_key: str
    organization: Optional[str] = None
    default_model: str = "gpt-3.5-turbo"
    max_tokens: int = 4096
    temperature: float = 0.7
    
    @field_validator('api_key')
    @classmethod
    def validate_api_key(cls, v):
        assert v, "OpenAI API key is required"
        return v
    
    model_config = ConfigDict(env_prefix="OPENAI_") 