import json

from fastapi import FastAPI
from fastapi.testclient import TestClient

from nuclei_backend.users.main import users_router

app = FastAPI()
app.include_router(users_router)

client = TestClient(app)


def test_login_for_access_token():
    data = {"username": "testuser", "password": "testpassword"}
    response = client.post("/user/token", data=data)
    assert response.status_code == 200
    response_data = json.loads(response.content)
    assert "access_token" in response_data
    assert "token_type" in response_data
    assert response_data["token_type"] == "bearer"


def test_login_for_access_token_failed():
    data = {"username": "wronguser", "password": "wrongpassword"}
    response = client.post("/user/token", data=data)
    assert response.status_code == 401
    assert "Incorrect username or password" in response.content


def test_read_users_me():
    # first call the login endpoint to get the access token
    data = {"username": "testuser", "password": "testpassword"}
    response = client.post("/user/token", data=data)
    response_data = json.loads(response.content)
    access_token = response_data["access_token"]

    # then call the /me endpoint with the access token
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/user/me", headers=headers)
    assert response.status_code == 200
    assert "testuser" in response.content
