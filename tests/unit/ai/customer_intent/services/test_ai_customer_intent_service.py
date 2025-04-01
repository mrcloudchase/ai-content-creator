import pytest
from app.ai.customer_intent.services.ai_customer_intent_service import CustomerIntentService


class TestCustomerIntentService:
    """Tests for the CustomerIntentService class"""

    def test_init(self):
        """Test initialization"""
        service = CustomerIntentService()
        assert isinstance(service, CustomerIntentService)

    def test_format_customer_intent_prompt_basic(self):
        """Test basic prompt formatting without user type"""
        # Setup
        service = CustomerIntentService()
        document_text = "This is a test document for customer intent analysis."
        
        # Execute
        result = service.format_customer_intent_prompt(document_text)
        
        # Verify
        assert "messages" in result
        messages = result["messages"]
        assert len(messages) == 2
        
        # Verify system message
        assert messages[0]["role"] == "system"
        assert "expert at analyzing documents" in messages[0]["content"]
        assert "As a [user type], I want to [action] because [reason]" in messages[0]["content"]
        
        # Verify user message
        assert messages[1]["role"] == "user"
        assert "analyze the following document" in messages[1]["content"]
        assert document_text in messages[1]["content"]
        assert "user type" not in messages[1]["content"].lower()

    def test_format_customer_intent_prompt_with_user_type(self):
        """Test prompt formatting with specified user type"""
        # Setup
        service = CustomerIntentService()
        document_text = "This is a test document for customer intent analysis."
        user_type = "product manager"
        
        # Execute
        result = service.format_customer_intent_prompt(document_text, user_type)
        
        # Verify
        assert "messages" in result
        messages = result["messages"]
        
        # Verify user message contains user_type
        assert messages[1]["role"] == "user"
        assert f"for a {user_type}" in messages[1]["content"]
        assert document_text in messages[1]["content"]

    def test_format_customer_intent_prompt_with_empty_document(self):
        """Test prompt formatting with empty document raises error"""
        # Setup
        service = CustomerIntentService()
        
        # Execute & Verify
        with pytest.raises(ValueError) as excinfo:
            service.format_customer_intent_prompt("")
        
        assert "Document text cannot be empty" in str(excinfo.value)

    def test_format_customer_intent_prompt_with_whitespace_document(self):
        """Test prompt formatting with whitespace-only document raises error"""
        # Setup
        service = CustomerIntentService()
        
        # Execute & Verify
        with pytest.raises(ValueError) as excinfo:
            service.format_customer_intent_prompt("   \n   ")
        
        assert "Document text cannot be empty" in str(excinfo.value)

    def test_system_message_content(self):
        """Test that system message contains all required guidelines"""
        # Setup
        service = CustomerIntentService()
        document_text = "Test document"
        
        # Execute
        result = service.format_customer_intent_prompt(document_text)
        
        # Verify system message content
        system_content = result["messages"][0]["content"]
        
        # Check that system message contains the key components
        assert "As a [user type], I want to [action] because [reason]" in system_content
        assert "User type should be specific" in system_content
        assert "Action should be clear" in system_content
        assert "Reason should explain" in system_content
        assert "Keep the statement concise" in system_content
        assert "Focus on the user's perspective" in system_content
        assert "Avoid technical jargon" in system_content
        assert "Make the intent actionable" in system_content
        assert "<customer_intent>" in system_content
        
        # Check for examples
        assert "Example good customer intents" in system_content
        assert "Example bad customer intents" in system_content
        assert "too vague" in system_content
