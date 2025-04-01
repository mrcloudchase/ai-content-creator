import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from app.main import app


class TestMainApp:
    """Tests for the main FastAPI application"""
    
    def test_app_initialization(self):
        """Test that the app is initialized correctly"""
        assert app.title == "AI Content Developer API"
        assert app.description == "API application for generating AI content"
        assert app.version is not None
        
        # Check that routers are included
        routes = [route.path for route in app.routes]
        assert "/api/v1/customer-intent" in routes
        assert "/health" in routes
        assert "/" in routes
    
    def test_root_endpoint(self, client):
        """Test the root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "AI Content Developer API"
        assert "version" in data
        assert data["documentation"] == "/docs"
        assert "endpoints" in data
        assert "customer_intent" in data["endpoints"]
    
    def test_health_endpoint(self, client):
        """Test the health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "ai-content-developer-api"
        assert "version" in data
