from typing import Dict, Any, Optional, List
import os
import openai
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
import traceback

class OpenAIServiceError(Exception):
    """Custom exception for OpenAI service errors"""
    pass

class AIService:
    """
    Service for interacting with OpenAI APIs (both regular and Azure)
    """
    
    def __init__(self, settings=None):
        """
        Initialize the OpenAI service with settings
        
        Args:
            settings: Optional settings object with API configuration
        """
        self.settings = settings
        
        # Determine mode based on settings
        self.use_azure = False
        if settings and settings.use_azure:
            self.use_azure = True
            print(f"Using Azure OpenAI configuration")
        else:
            print(f"Using standard OpenAI configuration")
        
        # Create the appropriate client
        self._setup_client()
    
    def _setup_client(self):
        """Set up the appropriate OpenAI client based on configuration"""
        if self.use_azure:
            self._setup_azure_client()
        else:
            self._setup_openai_client()
    
    def _setup_openai_client(self):
        """Set up standard OpenAI client"""
        # Get API key from settings or environment
        api_key = self.settings.api_key if self.settings else os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            print("Warning: No OpenAI API key provided, but continuing in case Azure mode is enabled")
        
        # Mask key for logging if present
        if api_key:
            masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
            print(f"Using OpenAI API key: {masked_key}")
        
        # Get organization from settings or environment (optional)
        org = self.settings.organization if self.settings and self.settings.organization else os.getenv("OPENAI_ORGANIZATION")
        
        # Create the async client
        self.client = openai.AsyncOpenAI(
            api_key=api_key,
            organization=org
        )
        print(f"Created AsyncOpenAI client: {type(self.client)}")
    
    def _setup_azure_client(self):
        """Set up Azure OpenAI client with managed identity"""
        try:
            # Get Azure settings from settings object or environment
            azure_endpoint = self.settings.azure_endpoint if self.settings else os.getenv("AZURE_OPENAI_ENDPOINT")
            
            if not azure_endpoint:
                print("No Azure OpenAI endpoint provided!")
                raise OpenAIServiceError("No Azure OpenAI endpoint provided")
                
            print(f"Using Azure OpenAI endpoint: {azure_endpoint}")
            
            # Create the credential
            credential = DefaultAzureCredential()
            print("Created DefaultAzureCredential")
            
            # Create a token provider function with the proper scope
            token_provider = get_bearer_token_provider(
                credential, 
                "https://cognitiveservices.azure.com/.default"
            )
            print("Created token provider for Azure OpenAI")
            
            # Get API version from settings or environment
            api_version = (
                self.settings.azure_api_version if self.settings 
                else os.getenv("AZURE_OPENAI_API_VERSION", "2023-12-01-preview")
            )
            
            # Create the Azure OpenAI client
            self.client = openai.AsyncAzureOpenAI(
                azure_endpoint=azure_endpoint,
                api_version=api_version,
                azure_ad_token_provider=token_provider
            )
            print(f"Created AsyncAzureOpenAI client with managed identity")
            
        except Exception as e:
            print(f"Error setting up Azure OpenAI client: {str(e)}")
            print(f"Error traceback: {traceback.format_exc()}")
            raise OpenAIServiceError(f"Failed to initialize Azure OpenAI client: {str(e)}")
    
    async def generate_completion(self, 
                           messages: List[Dict[str, str]],
                           model: Optional[str] = None,
                           max_tokens: Optional[int] = None,
                           temperature: Optional[float] = None) -> Dict[str, Any]:
        """
        Generate a completion from OpenAI or Azure OpenAI
        
        Args:
            messages: List of message dictionaries with role and content
            model: Optional model to use (ignored for Azure, which uses deployments)
            max_tokens: Optional max tokens parameter
            temperature: Optional temperature parameter
            
        Returns:
            Dictionary containing generated text and usage statistics
            
        Raises:
            OpenAIServiceError: If there's an error calling the API
        """
        try:
            # Log which service we're using
            service_name = "Azure OpenAI" if self.use_azure else "OpenAI"
            print(f"Generating completion using {service_name}")
            
            # Build base parameters that work for both APIs
            params = {
                "messages": messages
            }
            
            # Handle model parameter differently for Azure vs. regular OpenAI
            if self.use_azure:
                # For Azure, use deployment name as the model parameter
                deployment = (
                    self.settings.azure_deployment_name if self.settings 
                    else os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
                )
                if not deployment:
                    raise OpenAIServiceError("Azure OpenAI deployment name not provided")
                    
                print(f"Using Azure deployment as model: {deployment}")
                params["model"] = deployment  # Pass deployment name to the model parameter
            else:
                # For regular OpenAI, use the model parameter as before
                selected_model = model or (self.settings.default_model if self.settings else "gpt-4")
                print(f"Using model: {selected_model}")
                params["model"] = selected_model
            
            # Add optional parameters if provided
            if temperature is not None:
                params["temperature"] = temperature
                
            if max_tokens is not None:
                params["max_tokens"] = max_tokens
            
            # Log the API call (without messages for brevity)
            param_log = params.copy()
            param_log["messages"] = f"[{len(messages)} messages]"
            print(f"API parameters: {param_log}")
            
            # Call the OpenAI API - same method signature for both clients
            response = await self.client.chat.completions.create(**params)
            print("Successfully called chat.completions.create()")
            
            # Build the result - same structure for both APIs
            result = {
                "text": response.choices[0].message.content,
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
            print(f"Response usage: {result['usage']}")
            return result
            
        except Exception as e:
            print(f"Error type: {type(e)}")
            print(f"Error message: {str(e)}")
            print(f"Error traceback: {traceback.format_exc()}")
            raise OpenAIServiceError(f"Error calling {service_name} API: {str(e)}") 