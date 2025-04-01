import pytest
from pydantic import ValidationError

from app.ai.customer_intent.models.ai_customer_intent_model import CustomerIntentResponse


class TestCustomerIntentModel:
    """Tests for the CustomerIntentResponse model"""
    
    def test_valid_customer_intent_response(self):
        """Test creating a valid CustomerIntentResponse model"""
        # Valid data
        valid_data = {
            "intent": "As a content creator, I want to streamline my workflow because it saves time and increases productivity.",
            "model": "gpt-4",
            "model_family": "gpt",
            "capabilities": {
                "supports_functions": True,
                "supports_vision": False,
                "supports_embeddings": True
            },
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150
            },
            "token_limit": 4096,
            "token_count": 100,
            "remaining_tokens": 3996,
            "text_used": "This is the processed text that was used to generate the intent."
        }
        
        # Create model instance
        response = CustomerIntentResponse(**valid_data)
        
        # Verify fields
        assert response.intent == valid_data["intent"]
        assert response.model == valid_data["model"]
        assert response.model_family == valid_data["model_family"]
        assert response.capabilities == valid_data["capabilities"]
        assert response.usage == valid_data["usage"]
        assert response.token_limit == valid_data["token_limit"]
        assert response.token_count == valid_data["token_count"]
        assert response.remaining_tokens == valid_data["remaining_tokens"]
        assert response.text_used == valid_data["text_used"]
    
    def test_missing_required_fields(self):
        """Test validation error when required fields are missing"""
        # Missing required fields
        invalid_data = {
            "model": "gpt-4",
            "model_family": "gpt",
            "capabilities": {},
            "usage": {"total_tokens": 150},
            "token_limit": 4096,
            "remaining_tokens": 3996
            # Missing: intent, token_count, text_used
        }
        
        # Attempt to create model instance
        with pytest.raises(ValidationError) as excinfo:
            CustomerIntentResponse(**invalid_data)
        
        # Verify error contains information about missing fields
        error_str = str(excinfo.value)
        assert "intent" in error_str  # Missing intent field
        assert "token_count" in error_str  # Missing token_count field
        assert "text_used" in error_str  # Missing text_used field
    
    def test_invalid_field_types(self):
        """Test validation error when field types are invalid"""
        # Invalid field types
        invalid_data = {
            "intent": "As a content creator, I want to streamline my workflow.",
            "model": "gpt-4",
            "model_family": "gpt",
            "capabilities": "not a dict",  # Should be a dict
            "usage": {
                "prompt_tokens": "100",  # Should be int
                "completion_tokens": 50,
                "total_tokens": 150
            },
            "token_limit": "4096",  # Should be int
            "token_count": 100,
            "remaining_tokens": 3996,
            "text_used": "This is the processed text."
        }
        
        # Attempt to create model instance
        with pytest.raises(ValidationError) as excinfo:
            CustomerIntentResponse(**invalid_data)
        
        # Verify error contains information about type validation
        error_str = str(excinfo.value)
        assert "capabilities" in error_str
        assert "type=dict_type" in error_str or "type=dict" in error_str
        
    def test_model_serialization(self):
        """Test serializing the model to JSON/dict"""
        # Create a valid model
        response = CustomerIntentResponse(
            intent="As a content creator, I want to streamline my workflow because it saves time.",
            model="gpt-4",
            model_family="gpt",
            capabilities={"supports_functions": True},
            usage={"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150},
            token_limit=4096,
            token_count=100,
            remaining_tokens=3996,
            text_used="Test text."
        )
        
        # Serialize to dict
        response_dict = response.model_dump()
        
        # Verify serialization
        assert isinstance(response_dict, dict)
        assert response_dict["intent"] == "As a content creator, I want to streamline my workflow because it saves time."
        assert response_dict["model"] == "gpt-4"
        assert response_dict["model_family"] == "gpt"
        assert response_dict["capabilities"] == {"supports_functions": True}
        assert response_dict["usage"] == {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150}
        assert response_dict["token_limit"] == 4096
        assert response_dict["token_count"] == 100
        assert response_dict["remaining_tokens"] == 3996
        assert response_dict["text_used"] == "Test text."
