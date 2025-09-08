import os
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine

Base.metadata.create_all(bind=engine)
client = TestClient(app)

def auth_token():
    client.post("/auth/signup", json={
        "email": "u@x.com", "password": "password123", "full_name": "User X"
    })
    r = client.post("/auth/login", json={"email": "u@x.com", "password": "password123"})
    return r.json()["access_token"]

def test_project_task_crud():
    token = auth_token()
    H = {"Authorization": f"Bearer {token}"}

    # Create project
    r = client.post("/projects", headers=H, json={"name": "Demo", "description": "desc"})
    assert r.status_code == 201
    pid = r.json()["id"]

    # Duplicate name blocked
    r = client.post("/projects", headers=H, json={"name": "Demo"})
    assert r.status_code == 409

    # List projects
    r = client.get("/projects?limit=5&offset=0", headers=H)
    assert r.status_code == 200
    assert len(r.json()) == 1

    # Create task
    r = client.post("/tasks", headers=H, json={
        "title": "First task", "project_id": pid, "description": "do it", "done": False
    })
    assert r.status_code == 201
    tid = r.json()["id"]

    # Update task -> done
    r = client.put(f"/tasks/{tid}", headers=H, json={"done": True})
    assert r.status_code == 200
    assert r.json()["done"] is True

    # Filter tasks by project
    r = client.get(f"/tasks?project_id={pid}&done=true", headers=H)
    assert r.status_code == 200
    assert len(r.json()) == 1

    # Cascade: delete project removes tasks
    r = client.delete(f"/projects/{pid}", headers=H)
    assert r.status_code == 204

    r = client.get(f"/tasks/{tid}", headers=H)
    assert r.status_code == 404
