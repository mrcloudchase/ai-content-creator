from typing import Dict, Any, List
from app.ai.content_types.models.content_types_config import CONTENT_TYPES

class ContentGenerateService:
    """Service for content generation operations"""
    
    def format_content_generate_prompt(self, 
                                      content_type: str, 
                                      intent: str, 
                                      text: str,
                                      title: str = None) -> Dict[str, Any]:
        """
        Format the prompt for content generation for a specific content type
        
        Args:
            content_type: The content type to generate (tutorial, how-to, explanation, reference)
            intent: The customer intent statement
            text: The source text to use
            title: Optional title for the content
            
        Returns:
            Formatted prompt for the LLM
        """
        # Input validation
        if content_type not in CONTENT_TYPES:
            raise ValueError(f"Invalid content type: {content_type}")
        if not intent or not intent.strip():
            raise ValueError("Intent cannot be empty")
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        # Get content type details
        type_info = CONTENT_TYPES[content_type]
        type_name = type_info["name"]
        type_description = type_info["description"]
        type_purpose = type_info["purpose"]
        type_template = type_info["markdown_template"]
        
        # Create a system prompt that explains the task
        system_prompt = f"""
        You are an AI content creation assistant specialized in creating {type_name} content.
        
        About this content type:
        - Name: {type_name}
        - Description: {type_description}
        - Purpose: {type_purpose}
        
        Your task is to create {type_name} content based on:
        1. The customer intent statement
        2. The provided source text
        3. The markdown template structure shown below
        
        Template structure:
        ```markdown
        {type_template}
        ```
        
        Guidelines:
        - Create high-quality, comprehensive content that fulfills the purpose of a {type_name}
        - Use the provided template structure, but adapt section headers as needed
        - Fill in all placeholder content with relevant, detailed information
        - Use information from the source text where applicable
        - Keep the tone professional and informative
        - Use proper markdown formatting including code blocks, lists, and tables as appropriate
        - If a title is provided, use it; otherwise, create an appropriate title
        - Generate content that completely fulfills the customer intent
        
        Return only the final markdown content with no additional text.
        """
        
        # Create a user prompt with the intent, text and title
        title_text = f"Title: {title}" if title else "Please create an appropriate title"
        user_prompt = f"""
        Customer Intent: {intent}
        
        {title_text}
        
        Source Text:
        {text}
        
        Please generate {type_name} content following the template structure.
        """
        
        # Return the formatted messages
        return {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        } 