from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def test_create_crew(client: TestClient, db_session: Session):
    response = client.post("/crews/", json={"name": "Test Crew"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Crew"
    assert "id" in data

def test_read_crews(client: TestClient, db_session: Session):
    client.post("/crews/", json={"name": "Test Crew 1"})
    client.post("/crews/", json={"name": "Test Crew 2"})
    response = client.get("/crews/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Test Crew 1"
    assert data[1]["name"] == "Test Crew 2"

def test_read_crew(client: TestClient, db_session: Session):
    response = client.post("/crews/", json={"name": "Test Crew"})
    crew_id = response.json()["id"]
    response = client.get(f"/crews/{crew_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Crew"
    assert data["id"] == crew_id

def test_update_crew(client: TestClient, db_session: Session):
    response = client.post("/crews/", json={"name": "Test Crew"})
    crew_id = response.json()["id"]
    response = client.put(f"/crews/{crew_id}", json={"name": "Updated Crew"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Crew"
    assert data["id"] == crew_id

def test_delete_crew(client: TestClient, db_session: Session):
    response = client.post("/crews/", json={"name": "Test Crew"})
    crew_id = response.json()["id"]
    response = client.delete(f"/crews/{crew_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Crew"
    assert data["id"] == crew_id
    response = client.get(f"/crews/{crew_id}")
    assert response.status_code == 404
