from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def test_create_agent(client: TestClient, db_session: Session):
    crew_response = client.post("/crews/", json={"name": "Test Crew"})
    crew_id = crew_response.json()["id"]
    response = client.post(
        "/agents/",
        json={
            "name": "Test Agent",
            "role": "worker",
            "system_prompt": "You are a test agent.",
            "crew_id": crew_id,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Agent"
    assert data["role"] == "worker"
    assert data["system_prompt"] == "You are a test agent."
    assert data["crew_id"] == crew_id
    assert "id" in data

def test_read_agents(client: TestClient, db_session: Session):
    crew_response = client.post("/crews/", json={"name": "Test Crew"})
    crew_id = crew_response.json()["id"]
    client.post(
        "/agents/",
        json={
            "name": "Test Agent 1",
            "role": "worker",
            "system_prompt": "You are a test agent.",
            "crew_id": crew_id,
        },
    )
    client.post(
        "/agents/",
        json={
            "name": "Test Agent 2",
            "role": "worker",
            "system_prompt": "You are a test agent.",
            "crew_id": crew_id,
        },
    )
    response = client.get("/agents/")
    assert response.status_code == 200
    data = response.json()
    # Should have 3 agents: supervisor (auto-created) + 2 test agents
    assert len(data) == 3
    # Find the test agents (excluding supervisor)
    test_agents = [agent for agent in data if agent["role"] != "supervisor"]
    assert len(test_agents) == 2
    assert test_agents[0]["name"] == "Test Agent 1"
    assert test_agents[1]["name"] == "Test Agent 2"

def test_read_agent(client: TestClient, db_session: Session):
    crew_response = client.post("/crews/", json={"name": "Test Crew"})
    crew_id = crew_response.json()["id"]
    response = client.post(
        "/agents/",
        json={
            "name": "Test Agent",
            "role": "worker",
            "system_prompt": "You are a test agent.",
            "crew_id": crew_id,
        },
    )
    agent_id = response.json()["id"]
    response = client.get(f"/agents/{agent_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Agent"
    assert data["id"] == agent_id

def test_update_agent(client: TestClient, db_session: Session):
    crew_response = client.post("/crews/", json={"name": "Test Crew"})
    crew_id = crew_response.json()["id"]
    response = client.post(
        "/agents/",
        json={
            "name": "Test Agent",
            "role": "worker",
            "system_prompt": "You are a test agent.",
            "crew_id": crew_id,
        },
    )
    agent_id = response.json()["id"]
    response = client.put(
        f"/agents/{agent_id}",
        json={
            "name": "Updated Agent",
            "role": "supervisor",
            "system_prompt": "You are an updated test agent.",
            "crew_id": crew_id,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Agent"
    assert data["role"] == "supervisor"
    assert data["system_prompt"] == "You are an updated test agent."
    assert data["id"] == agent_id

def test_delete_agent(client: TestClient, db_session: Session):
    crew_response = client.post("/crews/", json={"name": "Test Crew"})
    crew_id = crew_response.json()["id"]
    response = client.post(
        "/agents/",
        json={
            "name": "Test Agent",
            "role": "worker",
            "system_prompt": "You are a test agent.",
            "crew_id": crew_id,
        },
    )
    agent_id = response.json()["id"]
    response = client.delete(f"/agents/{agent_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Agent"
    assert data["id"] == agent_id
    response = client.get(f"/agents/{agent_id}")
    assert response.status_code == 404
