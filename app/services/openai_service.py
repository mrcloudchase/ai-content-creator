from typing import Dict, Any, Optional, List
from openai import OpenAI, AsyncOpenAI
from app.config.settings import OpenAISettings

class OpenAIServiceError(Exception):
    """Custom exception for OpenAI service errors"""
    pass

class OpenAIService:
    """Service for interacting with OpenAI API"""
    
    def __init__(self, settings: Optional[OpenAISettings] = None):
        self.settings = settings or OpenAISettings()
        # Create client with proper authentication
        self.client = AsyncOpenAI(
            api_key=self.settings.api_key,
            organization=self.settings.organization
        )
    
    async def generate_completion(self, 
                         prompt: str,
                         model: Optional[str] = None,
                         max_tokens: Optional[int] = None,
                         temperature: Optional[float] = None) -> Dict[str, Any]:
        """
        Generate a completion from OpenAI
        
        Args:
            prompt: The prompt to send to OpenAI
            model: Optional model to use
            max_tokens: Optional max tokens parameter
            temperature: Optional temperature parameter
            
        Returns:
            Dictionary containing generated text and usage statistics
            
        Raises:
            OpenAIServiceError: If there's an error calling OpenAI
        """
        # Input validation with assertions
        assert prompt, "Prompt cannot be empty"
        
        try:
            # Prepare the messages in the format expected by OpenAI
            messages = [{"role": "user", "content": prompt}]
            
            # Call the OpenAI API with the client
            response = await self.client.chat.completions.create(
                model=model or self.settings.default_model,
                messages=messages,
                max_tokens=max_tokens or self.settings.max_tokens,
                temperature=temperature or self.settings.temperature
            )
            
            # Extract the response content
            content = response.choices[0].message.content
            
            # Output validation
            assert content, "Empty response from OpenAI"
            
            # Build result with usage statistics
            result = {
                "text": content,
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
            return result
        except AssertionError:
            raise
        except Exception as e:
            raise OpenAIServiceError(f"Error calling OpenAI API: {str(e)}") 