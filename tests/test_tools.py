from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def test_create_tool(client: TestClient, db_session: Session):
    mcp_server_response = client.post(
        "/mcp_servers/",
        json={"name": "Test MCP Server", "url": "http://localhost:8001"},
    )
    mcp_server_id = mcp_server_response.json()["id"]
    response = client.post(
        "/tools/",
        json={
            "name": "Test Tool",
            "description": "A tool for testing.",
            "mcp_server_id": mcp_server_id,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Tool"
    assert data["description"] == "A tool for testing."
    assert "id" in data

def test_read_tools(client: TestClient, db_session: Session):
    mcp_server_response = client.post(
        "/mcp_servers/",
        json={"name": "Test MCP Server", "url": "http://localhost:8001"},
    )
    mcp_server_id = mcp_server_response.json()["id"]
    client.post(
        "/tools/",
        json={
            "name": "Test Tool 1",
            "description": "A tool for testing.",
            "mcp_server_id": mcp_server_id,
        },
    )
    client.post(
        "/tools/",
        json={
            "name": "Test Tool 2",
            "description": "A tool for testing.",
            "mcp_server_id": mcp_server_id,
        },
    )
    response = client.get("/tools/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Test Tool 1"
    assert data[1]["name"] == "Test Tool 2"

def test_read_tool(client: TestClient, db_session: Session):
    mcp_server_response = client.post(
        "/mcp_servers/",
        json={"name": "Test MCP Server", "url": "http://localhost:8001"},
    )
    mcp_server_id = mcp_server_response.json()["id"]
    response = client.post(
        "/tools/",
        json={
            "name": "Test Tool",
            "description": "A tool for testing.",
            "mcp_server_id": mcp_server_id,
        },
    )
    tool_id = response.json()["id"]
    response = client.get(f"/tools/{tool_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Tool"
    assert data["id"] == tool_id

def test_update_tool(client: TestClient, db_session: Session):
    mcp_server_response = client.post(
        "/mcp_servers/",
        json={"name": "Test MCP Server", "url": "http://localhost:8001"},
    )
    mcp_server_id = mcp_server_response.json()["id"]
    response = client.post(
        "/tools/",
        json={
            "name": "Test Tool",
            "description": "A tool for testing.",
            "mcp_server_id": mcp_server_id,
        },
    )
    tool_id = response.json()["id"]
    response = client.put(
        f"/tools/{tool_id}",
        json={
            "name": "Updated Tool",
            "description": "An updated tool for testing.",
            "mcp_server_id": mcp_server_id,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Tool"
    assert data["description"] == "An updated tool for testing."
    assert data["id"] == tool_id

def test_delete_tool(client: TestClient, db_session: Session):
    mcp_server_response = client.post(
        "/mcp_servers/",
        json={"name": "Test MCP Server", "url": "http://localhost:8001"},
    )
    mcp_server_id = mcp_server_response.json()["id"]
    response = client.post(
        "/tools/",
        json={
            "name": "Test Tool",
            "description": "A tool for testing.",
            "mcp_server_id": mcp_server_id,
        },
    )
    tool_id = response.json()["id"]
    response = client.delete(f"/tools/{tool_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Tool"
    assert data["id"] == tool_id
    response = client.get(f"/tools/{tool_id}")
    assert response.status_code == 404
