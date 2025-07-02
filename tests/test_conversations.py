from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def test_create_conversation(client: TestClient, db_session: Session):
    crew_response = client.post("/crews/", json={"name": "Test Crew"})
    crew_id = crew_response.json()["id"]
    agent_response = client.post(
        "/agents/",
        json={
            "name": "Test Agent",
            "role": "worker",
            "system_prompt": "You are a test agent.",
            "crew_id": crew_id,
        },
    )
    agent_id = agent_response.json()["id"]
    response = client.post(
        "/conversations/",
        json={
            "user_input": "Hello",
            "agent_output": "Hi",
            "crew_id": crew_id,
            "agent_id": agent_id,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user_input"] == "Hello"
    assert data["agent_output"] == "Hi"
    assert data["crew_id"] == crew_id
    assert data["agent_id"] == agent_id
    assert "id" in data

def test_read_conversations(client: TestClient, db_session: Session):
    crew_response = client.post("/crews/", json={"name": "Test Crew"})
    crew_id = crew_response.json()["id"]
    agent_response = client.post(
        "/agents/",
        json={
            "name": "Test Agent",
            "role": "worker",
            "system_prompt": "You are a test agent.",
            "crew_id": crew_id,
        },
    )
    agent_id = agent_response.json()["id"]
    client.post(
        "/conversations/",
        json={
            "user_input": "Hello",
            "agent_output": "Hi",
            "crew_id": crew_id,
            "agent_id": agent_id,
        },
    )
    client.post(
        "/conversations/",
        json={
            "user_input": "How are you?",
            "agent_output": "I'm fine, thank you.",
            "crew_id": crew_id,
            "agent_id": agent_id,
        },
    )
    response = client.get("/conversations/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["user_input"] == "Hello"
    assert data[1]["user_input"] == "How are you?"

def test_read_conversation(client: TestClient, db_session: Session):
    crew_response = client.post("/crews/", json={"name": "Test Crew"})
    crew_id = crew_response.json()["id"]
    agent_response = client.post(
        "/agents/",
        json={
            "name": "Test Agent",
            "role": "worker",
            "system_prompt": "You are a test agent.",
            "crew_id": crew_id,
        },
    )
    agent_id = agent_response.json()["id"]
    response = client.post(
        "/conversations/",
        json={
            "user_input": "Hello",
            "agent_output": "Hi",
            "crew_id": crew_id,
            "agent_id": agent_id,
        },
    )
    conversation_id = response.json()["id"]
    response = client.get(f"/conversations/{conversation_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["user_input"] == "Hello"
    assert data["id"] == conversation_id
