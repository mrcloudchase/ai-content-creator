from typing import Dict, Any, Optional, List
import os
import openai

class OpenAIServiceError(Exception):
    """Custom exception for OpenAI service errors"""
    pass

class AIService:
    """
    Service for interacting with OpenAI API
    Handles model-specific parameter differences automatically
    """
    
    def __init__(self, settings=None):
        """
        Initialize the OpenAI service with settings
        
        Args:
            settings: Optional settings object with API configuration
        """
        self.settings = settings
        
        # Debug the API key
        api_key = self.settings.api_key if settings else os.getenv("OPENAI_API_KEY")
        masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
        print(f"Using API key: {masked_key}")
        
        # Create the async client with proper authentication
        self.client = openai.AsyncOpenAI(
            api_key=api_key,
            organization=self.settings.organization if settings and settings.organization else None
        )
        print(f"Created AsyncOpenAI client: {type(self.client)}")
    
    async def generate_completion(self, 
                         messages: List[Dict[str, str]],
                         model: Optional[str] = None,
                         max_tokens: Optional[int] = None,
                         temperature: Optional[float] = None) -> Dict[str, Any]:
        """
        Generate a completion from OpenAI using chat completion
        
        Args:
            messages: List of message dictionaries with role and content
            model: Optional model to use
            max_tokens: Optional max tokens parameter
            temperature: Optional temperature parameter
            
        Returns:
            Dictionary containing generated text and usage statistics
            
        Raises:
            OpenAIServiceError: If there's an error calling OpenAI
        """
        try:
            # Get the model to use
            selected_model = model
            if not selected_model and self.settings:
                selected_model = self.settings.default_model
            
            print(f"Using model: {selected_model}")
            
            # TODO: Temporarily disabled temperature handling due to potential 
            # compatibility issues with different model versions. Will resolve when
            # implementing dynamic parameter handling for o-series vs gpt-series models.
            # 
            # Get temperature
            # selected_temp = temperature
            # if not selected_temp and self.settings:
            #     selected_temp = self.settings.temperature
                
            # Build base parameters
            params = {
                "model": selected_model,
                "messages": messages,
                # "temperature": selected_temp
            }
            
            # TODO: Temporarily disabled max_tokens/max_completion_tokens handling due to 
            # compatibility issues with different model versions. Need to implement a more
            # robust solution that works across all model types.
            # 
            # Handle the max tokens parameter based on model family
            # tokens_value = max_tokens
            # if not tokens_value and self.settings:
            #     tokens_value = self.settings.max_tokens
            #     
            # if tokens_value is not None:
            #     # Check if we're dealing with an o-series model (o1-mini, o1-preview, etc.)
            #     # These models require max_completion_tokens instead of max_tokens
            #     if selected_model and (selected_model.startswith(("o1-", "o3-", "o-")) or "-o" in selected_model):
            #         print(f"Using max_completion_tokens={tokens_value} for {selected_model}")
            #         params["max_completion_tokens"] = tokens_value
            #     else:
            #         print(f"Using max_tokens={tokens_value} for {selected_model}")
            #         params["max_tokens"] = tokens_value
            
            # Print the exact method we're about to call
            print(f"About to call: self.client.chat.completions.create()")
            print(f"With parameters: {params}")
            
            # Call the OpenAI API
            response = await self.client.chat.completions.create(**params)
            print("Successfully called chat.completions.create()")
            
            # Build the result
            result = {
                "text": response.choices[0].message.content,
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
            return result
        except Exception as e:
            print(f"Error type: {type(e)}")
            print(f"Error message: {str(e)}")
            raise OpenAIServiceError(f"Error calling OpenAI API: {str(e)}") 