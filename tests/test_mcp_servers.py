from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import patch

def test_create_mcp_server(client: TestClient, db_session: Session, auth_headers):
    response = client.post(
        "/mcp_servers/",
        json={"name": "Test MCP Server", "url": "http://localhost:8001"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test MCP Server"
    assert data["url"] == "http://localhost:8001"
    assert "id" in data

def test_read_mcp_servers(client: TestClient, db_session: Session, auth_headers):
    client.post(
        "/mcp_servers/",
        json={"name": "Test MCP Server 1", "url": "http://localhost:8001"},
        headers=auth_headers,
    )
    client.post(
        "/mcp_servers/",
        json={"name": "Test MCP Server 2", "url": "http://localhost:8002"},
        headers=auth_headers,
    )
    response = client.get("/mcp_servers/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Test MCP Server 1"
    assert data[1]["name"] == "Test MCP Server 2"

def test_read_mcp_server(client: TestClient, db_session: Session, auth_headers):
    response = client.post(
        "/mcp_servers/",
        json={"name": "Test MCP Server", "url": "http://localhost:8001"},
        headers=auth_headers,
    )
    mcp_server_id = response.json()["id"]
    response = client.get(f"/mcp_servers/{mcp_server_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test MCP Server"
    assert data["id"] == mcp_server_id

def test_update_mcp_server(client: TestClient, db_session: Session, auth_headers):
    response = client.post(
        "/mcp_servers/",
        json={"name": "Test MCP Server", "url": "http://localhost:8001"},
        headers=auth_headers,
    )
    mcp_server_id = response.json()["id"]
    response = client.put(
        f"/mcp_servers/{mcp_server_id}",
        json={"name": "Updated MCP Server", "url": "http://localhost:8002"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated MCP Server"
    assert data["url"] == "http://localhost:8002"
    assert data["id"] == mcp_server_id

def test_delete_mcp_server(client: TestClient, db_session: Session, auth_headers):
    response = client.post(
        "/mcp_servers/",
        json={"name": "Test MCP Server", "url": "http://localhost:8001"},
        headers=auth_headers,
    )
    mcp_server_id = response.json()["id"]
    response = client.delete(f"/mcp_servers/{mcp_server_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test MCP Server"
    assert data["id"] == mcp_server_id
    response = client.get(f"/mcp_servers/{mcp_server_id}", headers=auth_headers)
    assert response.status_code == 404

@patch("app.services.mcp_server.streamablehttp_client")
def test_get_mcp_server_tools(mock_streamablehttp_client, client: TestClient, db_session: Session, auth_headers):
    # Mock the streamablehttp_client to avoid actual network calls
    mock_streamablehttp_client.return_value.__aenter__.return_value = (
        None,
        None,
        None,
    )
    response = client.post(
        "/mcp_servers/",
        json={"name": "Test MCP Server", "url": "http://localhost:8001"},
        headers=auth_headers,
    )
    mcp_server_id = response.json()["id"]
    with patch("app.services.mcp_server.ClientSession") as mock_clientsession:
        mock_session = mock_clientsession.return_value.__aenter__.return_value
        mock_session.list_tools.return_value = [{"name": "test_tool"}]
        response = client.get(f"/mcp_servers/{mcp_server_id}/tools", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data == [{"name": "test_tool"}]
