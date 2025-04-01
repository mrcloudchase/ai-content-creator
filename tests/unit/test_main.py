import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    """Test the root endpoint returns the correct information."""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    
    # Check basic structure
    assert "name" in data
    assert "version" in data
    assert "documentation" in data
    assert "endpoints" in data
    
    # Check endpoints
    assert "health" in data["endpoints"]
    assert "api_base" in data["endpoints"]

def test_health_endpoint():
    """Test the health endpoint returns a healthy status."""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "healthy"
    assert "service" in data
    assert "version" in data

def test_api_endpoints():
    """Test that the API endpoints are properly configured."""
    # List all routes and check expected endpoints exist
    routes = [{"path": route.path, "methods": route.methods} for route in app.routes]
    
    # Check for customer intent routes
    customer_intent_routes = [route for route in routes if "/api/v1/customer-intent" in route["path"]]
    assert len(customer_intent_routes) > 0, "Customer intent routes should be registered"
    
    # Verify health endpoint
    health_routes = [route for route in routes if route["path"] == "/health"]
    assert len(health_routes) == 1
    assert "GET" in health_routes[0]["methods"]
