import pytest
from unittest.mock import patch
from app.ai.content_generate.services.content_generate_service import ContentGenerateService
from app.ai.content_types.models.content_types_config import CONTENT_TYPES

class TestContentGenerateService:
    """Unit tests for the ContentGenerateService class"""
    
    def setup_method(self):
        """Set up test dependencies"""
        self.service = ContentGenerateService()
        
    def test_format_content_generate_prompt_valid_input(self):
        """Test format_content_generate_prompt with valid input"""
        # Test data
        content_type = "tutorial"
        intent = "As a developer, I want to create a REST API because it will help me serve data to clients."
        text = "This is some sample text about building APIs with FastAPI."
        title = "Creating a REST API with FastAPI"
        
        # Call the method
        result = self.service.format_content_generate_prompt(
            content_type=content_type,
            intent=intent,
            text=text,
            title=title
        )
        
        # Assert result structure
        assert isinstance(result, dict)
        assert "messages" in result
        assert len(result["messages"]) == 2
        assert result["messages"][0]["role"] == "system"
        assert result["messages"][1]["role"] == "user"
        
        # Check content of system message
        system_message = result["messages"][0]["content"]
        assert CONTENT_TYPES[content_type]["name"] in system_message
        assert CONTENT_TYPES[content_type]["description"] in system_message
        assert CONTENT_TYPES[content_type]["purpose"] in system_message
        assert CONTENT_TYPES[content_type]["markdown_template"] in system_message
        
        # Check content of user message
        user_message = result["messages"][1]["content"]
        assert intent in user_message
        assert title in user_message
        assert text in user_message
        
    def test_format_content_generate_prompt_without_title(self):
        """Test format_content_generate_prompt without providing a title"""
        # Test data
        content_type = "how-to"
        intent = "As a user, I want to configure logging because it helps with debugging."
        text = "This is sample text about logging configuration."
        
        # Call the method without title
        result = self.service.format_content_generate_prompt(
            content_type=content_type,
            intent=intent,
            text=text
        )
        
        # Check user message contains default title prompt
        user_message = result["messages"][1]["content"]
        assert "Please create an appropriate title" in user_message
        
    def test_format_content_generate_prompt_invalid_content_type(self):
        """Test format_content_generate_prompt with invalid content type"""
        # Test data
        content_type = "invalid_type"
        intent = "Test intent"
        text = "Test text"
        
        # Assert raises ValueError
        with pytest.raises(ValueError) as excinfo:
            self.service.format_content_generate_prompt(
                content_type=content_type,
                intent=intent,
                text=text
            )
        
        # Check error message
        assert "Invalid content type" in str(excinfo.value)
        
    def test_format_content_generate_prompt_empty_intent(self):
        """Test format_content_generate_prompt with empty intent"""
        # Test data
        content_type = "tutorial"
        intent = ""
        text = "Test text"
        
        # Assert raises ValueError
        with pytest.raises(ValueError) as excinfo:
            self.service.format_content_generate_prompt(
                content_type=content_type,
                intent=intent,
                text=text
            )
        
        # Check error message
        assert "Intent cannot be empty" in str(excinfo.value)
        
    def test_format_content_generate_prompt_empty_text(self):
        """Test format_content_generate_prompt with empty text"""
        # Test data
        content_type = "tutorial"
        intent = "Test intent"
        text = ""
        
        # Assert raises ValueError
        with pytest.raises(ValueError) as excinfo:
            self.service.format_content_generate_prompt(
                content_type=content_type,
                intent=intent,
                text=text
            )
        
        # Check error message
        assert "Text cannot be empty" in str(excinfo.value)
        
    @pytest.mark.parametrize("content_type", list(CONTENT_TYPES.keys()))
    def test_format_content_generate_prompt_all_content_types(self, content_type):
        """Test format_content_generate_prompt with all content types"""
        # Test data
        intent = "As a user, I want to test all content types."
        text = "This is test text for content type testing."
        
        # Call the method
        result = self.service.format_content_generate_prompt(
            content_type=content_type,
            intent=intent,
            text=text
        )
        
        # Verify the result includes content type specific information
        system_message = result["messages"][0]["content"]
        assert CONTENT_TYPES[content_type]["name"] in system_message
        assert CONTENT_TYPES[content_type]["description"] in system_message 