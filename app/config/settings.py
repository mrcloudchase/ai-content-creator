from pydantic import field_validator, ConfigDict, Field, model_validator
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
    
    # Standard OpenAI settings
    api_key: Optional[str] = Field(None, validation_alias="OPENAI_API_KEY")
    organization: Optional[str] = Field(None, validation_alias="OPENAI_ORGANIZATION")
    default_model: str = Field("gpt-4", validation_alias="OPENAI_DEFAULT_MODEL")
    encoding: str = Field("cl100k_base")
    max_tokens: int = Field(4000, validation_alias="MAX_TOKENS")
    temperature: float = Field(0.7, validation_alias="OPENAI_TEMPERATURE")
    
    # Azure OpenAI settings
    azure_endpoint: Optional[str] = Field(None, validation_alias="AZURE_OPENAI_ENDPOINT")
    azure_deployment_name: Optional[str] = Field(None, validation_alias="AZURE_OPENAI_DEPLOYMENT_NAME")
    azure_api_version: str = Field("2023-12-01-preview", validation_alias="AZURE_OPENAI_API_VERSION")
    
    # Configuration mode detection
    @property
    def use_azure(self) -> bool:
        """Determine if we should use Azure OpenAI based on available configuration"""
        return bool(self.azure_endpoint and self.azure_deployment_name)
    
    # Model validator to ensure at least one auth method is configured
    @model_validator(mode='after')
    def validate_auth_config(self):
        """Validate that either OpenAI API key or Azure OpenAI settings are provided"""
        has_openai_auth = bool(self.api_key)
        has_azure_auth = bool(self.azure_endpoint and self.azure_deployment_name)
        
        if not (has_openai_auth or has_azure_auth):
            raise ValueError(
                "Either OpenAI API key or Azure OpenAI credentials (endpoint + deployment name) must be provided"
            )
        
        return self
    
    @property
    def model_config(self) -> Dict[str, Any]:
        """Dynamic model configuration based on selected provider"""
        # Base configuration that works for both
        config = {
            "model": self.default_model,
            "encoding": self.encoding,
            "max_tokens": self.max_tokens,
            "context_window": 8192,  # Default - can be different per model
            "model_family": "gpt-4",  # Default
            "capabilities": {
                "vision": False,
                "function_calling": True,
                "json_mode": True,
            }
        }
        
        # Adjust config based on model name
        if "gpt-4" in self.default_model:
            config["model_family"] = "gpt-4"
            config["context_window"] = 8192
        elif "gpt-3.5" in self.default_model:
            config["model_family"] = "gpt-3.5-turbo"
            config["context_window"] = 4096
        
        # If using Azure, add deployment info
        if self.use_azure:
            config["azure_deployment"] = self.azure_deployment_name
            config["azure_endpoint"] = self.azure_endpoint
            config["azure_api_version"] = self.azure_api_version
        
        return config
    
    model_config = {
        "env_file": ".env",
        "extra": "ignore",  # Ignore extra env vars
        "protected_namespaces": ("settings_",)  # Avoid model_encoding conflict with model_ prefix
    }
    
    @property
    def model_family(self) -> str:
        """Get the model family (gpt, o1, o3, etc.)"""
        return self.default_model.split('-')[0]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print(f"OpenAISettings initialized with default_model: {self.default_model}")
        print(f"Environment variables loaded: OPENAI_DEFAULT_MODEL={os.environ.get('OPENAI_DEFAULT_MODEL')}")
        print(f"Model family: {self.model_family}")
        print(f"Using max_tokens parameter consistently across all model families")
    
    @property
    def model_settings(self) -> Dict[str, Any]:
        """Dynamically get configuration for the configured model"""
        try:
            # Get base model family
            model_family = self.default_model.split('-')[0]
            
            # Get encoding
            encoding = tiktoken.get_encoding(self.encoding)
            
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