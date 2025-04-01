from pydantic import field_validator, ConfigDict, Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from typing import Optional, Dict, Any
import tiktoken
import os

# Debug: Print current working directory and .env file location
print(f"Current working directory: {os.getcwd()}")
env_path = os.path.join(os.getcwd(), '.env')
print(f"Looking for .env file at: {env_path}")
print(f".env file exists: {os.path.exists(env_path)}")

# Load environment variables from .env file with override
load_dotenv(override=True)

# Debug: Print all environment variables
print("\nEnvironment variables:")
for key, value in os.environ.items():
    if key.startswith('OPENAI_'):
        print(f"{key}: {value}")

# Get the model from environment variable
DEFAULT_MODEL = os.getenv('OPENAI_DEFAULT_MODEL', 'gpt-4')
print(f"\nLoading model from .env: {DEFAULT_MODEL}")

class OpenAISettings(BaseSettings):
    """Settings for OpenAI API integration"""
    model_config = ConfigDict(env_prefix="OPENAI_")
    
    api_key: str
    organization: Optional[str] = None
    default_model: str = Field(default="gpt-4", env="DEFAULT_MODEL")
    temperature: float = 0.7
    max_tokens: int = 150
    
    @property
    def model_family(self) -> str:
        """Get the model family (gpt, o1, o3, etc.)"""
        return self.default_model.split('-')[0]
    
    @field_validator('api_key')
    @classmethod
    def validate_api_key(cls, v):
        assert v, "OpenAI API key is required"
        return v
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print(f"OpenAISettings initialized with default_model: {self.default_model}")
        print(f"Environment variables loaded: OPENAI_DEFAULT_MODEL={os.environ.get('OPENAI_DEFAULT_MODEL')}")
        print(f"Model family: {self.model_family}")
        print(f"Using max_tokens parameter consistently across all model families")
    
    @property
    def model_encoding(self) -> str:
        """Dynamically get encoding for the configured model"""
        try:
            # Try to get encoding directly from model name
            return tiktoken.encoding_for_model(self.default_model).name
        except Exception as e:
            # If that fails, try to determine encoding based on model family
            model_family = self.default_model.split('-')[0]
            if model_family in ['gpt']:
                return "cl100k_base"
            elif model_family in ['o1', 'o3']:
                return "cl100k_base"
            else:
                # Default to cl100k_base for unknown models
                return "cl100k_base"
    
    @property
    def model_settings(self) -> Dict[str, Any]:
        """Dynamically get configuration for the configured model"""
        try:
            # Get base model family
            model_family = self.default_model.split('-')[0]
            
            # Get encoding
            encoding = tiktoken.get_encoding(self.model_encoding)
            
            # Determine context window based on model family
            context_window = encoding.max_tokens
            
            # Build configuration
            config = {
                "encoding": encoding.name,
                "max_tokens": context_window,
                "context_window": context_window,
                "model": self.default_model,
                "model_family": model_family,
                "capabilities": self._get_model_capabilities(model_family)
            }
            
            return config
            
        except Exception as e:
            # Fallback configuration for unknown models
            return {
                "encoding": "cl100k_base",
                "max_tokens": 4096,
                "context_window": 4096,
                "model": self.default_model,
                "model_family": "unknown",
                "capabilities": self._get_model_capabilities("unknown")
            }
    
    def _get_model_capabilities(self, model_family: str) -> Dict[str, bool]:
        """Get model capabilities based on family"""
        capabilities = {
            "gpt": {
                "supports_functions": True,
                "supports_vision": False,
                "supports_embeddings": True
            },
            "o1": {
                "supports_functions": True,
                "supports_vision": True,
                "supports_embeddings": True
            },
            "o3": {
                "supports_functions": True,
                "supports_vision": True,
                "supports_embeddings": True
            },
            "unknown": {
                "supports_functions": False,
                "supports_vision": False,
                "supports_embeddings": False
            }
        }
        return capabilities.get(model_family, capabilities["unknown"]) 