import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_count_tokens_endpoint_simple_text():
    """Test the token counting endpoint with simple text"""
    # Arrange
    request_data = {
        "text": "Hello, world!"
    }
    
    # Act
    response = client.post("/api/v1/tokens/count", json=request_data)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "token_count" in data
    assert data["token_count"] > 0
    assert data["model"] == "gpt-3.5-turbo"
    assert data["model_limit"] == 4096
    assert data["percentage_used"] < 1  # Should be a very small percentage
    assert not data["is_near_limit"]
    assert not data["exceeds_limit"]
    assert data["tokens_remaining"] > 0

def test_count_tokens_endpoint_with_model():
    """Test the token counting endpoint with a specified model"""
    # Arrange
    request_data = {
        "text": "Hello, world!",
        "model": "gpt-4"
    }
    
    # Act
    response = client.post("/api/v1/tokens/count", json=request_data)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["model"] == "gpt-4"
    assert data["model_limit"] == 8192

def test_count_tokens_endpoint_longer_text():
    """Test the token counting endpoint with longer text"""
    # Arrange
    request_data = {
        "text": "This is a longer text. " * 100
    }
    
    # Act
    response = client.post("/api/v1/tokens/count", json=request_data)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["token_count"] > 100

def test_count_tokens_endpoint_empty_text():
    """Test the token counting endpoint with empty text"""
    # Arrange
    request_data = {
        "text": ""
    }
    
    # Act
    response = client.post("/api/v1/tokens/count", json=request_data)
    
    # Assert
    assert response.status_code == 400
    assert "Text cannot be empty" in response.json()["detail"]

def test_count_tokens_endpoint_multiline_text():
    """Test the token counting endpoint with multiline text"""
    # Arrange
    request_data = {
        "text": "This is line 1.\nThis is line 2.\nThis is line 3."
    }
    
    # Act
    response = client.post("/api/v1/tokens/count", json=request_data)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["token_count"] > 0 