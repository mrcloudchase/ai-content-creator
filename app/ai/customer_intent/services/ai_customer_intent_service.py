from typing import Optional, Dict, Any

class CustomerIntentService:
    """Service for creating prompts for customer intent generation"""
    
    def format_customer_intent_prompt(self, document_text: str, user_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Format the prompt for customer intent generation using best practices
        
        Args:
            document_text: The document text to use as the basis for the intent
            user_type: Optional specific user type to focus on
            
        Returns:
            Dictionary containing system message and user message for chat completion
        """
        # Input validation
        if not document_text or not document_text.strip():
            raise ValueError("Document text cannot be empty")
        
        # System message to set context and behavior
        system_message = """You are an expert at analyzing documents and creating clear, concise customer intent statements.
Your task is to create a customer intent statement that follows the format: "As a [user type], I want to [action] because [reason]"

Guidelines for creating customer intents:
1. User type should be specific and relevant to the document
2. Action should be clear, measurable, and achievable
3. Reason should explain the business value or motivation
4. Keep the statement concise but complete
5. Focus on the user's perspective and needs
6. Avoid technical jargon unless necessary
7. Make the intent actionable and testable
8. Only return the customer intent statement, inside <customer_intent> tags

Example good customer intents:
"As a content creator, I want to schedule posts in advance because it helps me maintain a consistent publishing schedule"
"As a project manager, I want to track team progress in real-time because it helps me identify and address bottlenecks early"

Example bad customer intents:
"As a user, I want to use the system because it's good" (too vague)
"As a developer, I want to implement features because the code needs it" (not user-focused)"""

        # User message with the document content
        user_message = f"""Please analyze the following document and create a customer intent statement following the format and guidelines above.

Document content:
{document_text}"""

        # If user_type is provided, add it to the user message
        if user_type:
            user_message = f"""Please analyze the following document and create a customer intent statement for a {user_type}, following the format and guidelines above.

Document content:
{document_text}"""

        # Return messages in OpenAI chat format
        return {
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ]
        } 