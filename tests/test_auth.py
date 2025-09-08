import os
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine

Base.metadata.create_all(bind=engine)
client = TestClient(app)

def test_signup_and_login_flow():
    r = client.post("/auth/signup", json={
        "email": "a@b.com", "password": "password123", "full_name": "Alice"
    })
    assert r.status_code == 201
    uid = r.json()["id"]
    assert uid > 0

    r = client.post("/auth/login", json={"email": "a@b.com", "password": "password123"})
    assert r.status_code == 200
    token = r.json()["access_token"]
    assert token

    r = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["email"] == "a@b.com"
