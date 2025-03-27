from app.services.openai_service import OpenAIService
from typing import Optional


class CustomerIntentService:
    """Service for generating customer intent statements based on document text"""
    
    def __init__(self, openai_service: OpenAIService):
        self.openai_service = openai_service
    
    def format_customer_intent_prompt(self, document_text: str, user_type: Optional[str] = None) -> str:
        """
        Format the prompt for customer intent generation
        
        Args:
            document_text: The document text to use as the basis for the intent
            user_type: Optional specific user type to focus on
            
        Returns:
            Formatted prompt ready for AI completion
        """
        base_prompt = "Write a customer intent in the following format: As a <type of user>, I want to do <what> because <why> based on the following info -\n\n"
        
        # If user_type is provided, customize the prompt
        if user_type:
            base_prompt = f"Write a customer intent for a {user_type} in the following format: As a {user_type}, I want to do <what> because <why> based on the following info -\n\n"
        
        # Combine with document text
        return f"{base_prompt}{document_text}"
    
    async def generate_customer_intent(self, document_text: str, user_type: Optional[str] = None, 
                                max_tokens: int = 150, temperature: float = 0.5) -> dict:
        """
        Generate a customer intent based on document content
        
        Args:
            document_text: The document text to use as basis for the intent
            user_type: Optional specific user type to focus on
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation (0.0-1.0)
            
        Returns:
            Dictionary containing the intent, model, and usage information
        """
        # Format the prompt
        prompt = self.format_customer_intent_prompt(document_text, user_type)
        
        # Call the OpenAI service
        completion = await self.openai_service.generate_completion(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        # Return formatted response
        return {
            "intent": completion["text"].strip(),
            "model": completion["model"],
            "usage": completion["usage"]
        } 