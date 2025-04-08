from typing import Dict, Any
from app.ai.content_types.models.content_types_config import CONTENT_TYPES

class ContentTypeService:
    """Service for content type selection operations"""
    
    def format_content_type_prompt(self, intent: str, text: str) -> dict:
        """
        Format the prompt for content type selection
        
        Args:
            intent: The customer intent statement
            text: The source text to analyze
            
        Returns:
            Formatted prompt for the LLM
        """
        # Generate content type descriptions by iterating through the CONTENT_TYPES dictionary
        content_type_descriptions = ""
        for type_key, type_info in CONTENT_TYPES.items():
            content_type_descriptions += f"\n{type_info['name']} ({type_key}):\n"
            content_type_descriptions += f"- Description: {type_info['description']}\n"
            content_type_descriptions += f"- Purpose: {type_info['purpose']}\n"
        
        # Create a system prompt that explains the task
        system_prompt = f"""
        You are an AI assistant specialized in content type selection based on the Diátaxis framework.
        Your task is to analyze the customer intent and source text to determine the most appropriate content type(s).
        
        The Diátaxis framework defines the following content types:
        {content_type_descriptions}
        
        Analyze the customer intent and source text, then select the most appropriate content type(s).
        For each selected type, provide a confidence score (0-100) and reasoning.
        
        Consider the following in your analysis:
        - The customer's explicit and implicit needs based on their intent statement
        - The nature of the source text and what it's trying to convey
        - The purpose of each content type and how well it matches the use case
        - Whether multiple content types might be appropriate (if so, rank them by confidence)
        
        Your response must be valid JSON in the following format:
        {{
            "content_types": [
                {{
                    "type": "tutorial",
                    "confidence": 85,
                    "reasoning": "Explanation of why this type is appropriate"
                }},
                ...
            ]
        }}
        """
        
        # Create a user prompt with the intent and text
        user_prompt = f"""
        Customer Intent: {intent}
        
        Source Text:
        {text}
        
        Based on the above customer intent and source text, determine the most appropriate content type(s) from the Diátaxis framework.
        """
        
        # Return the formatted messages
        return {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        } 