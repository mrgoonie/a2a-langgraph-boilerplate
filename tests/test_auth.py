import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def test_root_endpoint_no_auth_required(client: TestClient):
    """Test that the root endpoint doesn't require authentication."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "authentication" in data
    assert data["authentication"]["required"] is True

def test_crews_endpoint_requires_auth(client: TestClient):
    """Test that crews endpoint requires authentication."""
    response = client.get("/crews/")
    assert response.status_code == 401
    assert "API key required" in response.json()["detail"]

def test_crews_endpoint_with_valid_auth_header(client: TestClient):
    """Test crews endpoint with valid API key in header."""
    headers = {"X-API-Key": "development-api-key-please-change-in-production"}
    response = client.get("/crews/", headers=headers)
    assert response.status_code == 200

def test_crews_endpoint_with_valid_auth_query(client: TestClient):
    """Test crews endpoint with valid API key in query parameter."""
    response = client.get("/crews/?api_key=development-api-key-please-change-in-production")
    assert response.status_code == 200

def test_crews_endpoint_with_invalid_auth(client: TestClient):
    """Test crews endpoint with invalid API key."""
    headers = {"X-API-Key": "invalid-key"}
    response = client.get("/crews/", headers=headers)
    assert response.status_code == 401
    assert "Invalid API key" in response.json()["detail"]

def test_agents_endpoint_requires_auth(client: TestClient):
    """Test that agents endpoint requires authentication."""
    response = client.get("/agents/")
    assert response.status_code == 401

def test_agents_endpoint_with_valid_auth(client: TestClient):
    """Test agents endpoint with valid authentication."""
    headers = {"X-API-Key": "development-api-key-please-change-in-production"}
    response = client.get("/agents/", headers=headers)
    assert response.status_code == 200

def test_mcp_servers_endpoint_requires_auth(client: TestClient):
    """Test that MCP servers endpoint requires authentication."""
    response = client.get("/mcp_servers/")
    assert response.status_code == 401

def test_mcp_servers_endpoint_with_valid_auth(client: TestClient):
    """Test MCP servers endpoint with valid authentication."""
    headers = {"X-API-Key": "development-api-key-please-change-in-production"}
    response = client.get("/mcp_servers/", headers=headers)
    assert response.status_code == 200

def test_tools_endpoint_requires_auth(client: TestClient):
    """Test that tools endpoint requires authentication."""
    response = client.get("/tools/")
    assert response.status_code == 401

def test_tools_endpoint_with_valid_auth(client: TestClient):
    """Test tools endpoint with valid authentication."""
    headers = {"X-API-Key": "development-api-key-please-change-in-production"}
    response = client.get("/tools/", headers=headers)
    assert response.status_code == 200

def test_conversations_endpoint_requires_auth(client: TestClient):
    """Test that conversations endpoint requires authentication."""
    response = client.get("/conversations/")
    assert response.status_code == 401

def test_conversations_endpoint_with_valid_auth(client: TestClient):
    """Test conversations endpoint with valid authentication."""
    headers = {"X-API-Key": "development-api-key-please-change-in-production"}
    response = client.get("/conversations/", headers=headers)
    assert response.status_code == 200

def test_create_crew_with_auth(client: TestClient, db_session: Session):
    """Test creating a crew with authentication."""
    headers = {"X-API-Key": "development-api-key-please-change-in-production"}
    crew_data = {"name": "Test Crew"}
    response = client.post("/crews/", json=crew_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Crew"

def test_create_crew_without_auth(client: TestClient):
    """Test creating a crew without authentication."""
    crew_data = {"name": "Test Crew"}
    response = client.post("/crews/", json=crew_data)
    assert response.status_code == 401

def test_header_priority_over_query(client: TestClient):
    """Test that header API key takes priority over query parameter."""
    headers = {"X-API-Key": "development-api-key-please-change-in-production"}
    # Use invalid query param, but valid header - should succeed
    response = client.get("/crews/?api_key=invalid-key", headers=headers)
    assert response.status_code == 200

def test_auth_case_sensitivity(client: TestClient):
    """Test that API key validation is case-sensitive."""
    headers = {"X-API-Key": "DEVELOPMENT-API-KEY-PLEASE-CHANGE-IN-PRODUCTION"}  # Uppercase
    response = client.get("/crews/", headers=headers)
    assert response.status_code == 401  # Should fail due to case sensitivity