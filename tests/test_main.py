import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import engine
from sqlmodel import SQLModel


client = TestClient(app)


@pytest.fixture(scope="function")
def setup_and_teardown_db():
    # Drop and recreate all tables before each test
    SQLModel.metadata.drop_all(bind=engine)
    SQLModel.metadata.create_all(bind=engine)
    yield
    # Optionally, drop tables after test (for extra isolation)
    SQLModel.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def user_token(setup_and_teardown_db):
    # Register user (ignore if already exists)
    payload = {
        "email": "testuser3@example.com",
        "password": "testpassword",
        "name": "testuser3"
    }
    client.post("/auth/register", json=payload)
    # Login user
    login_payload = {
        "username": "testuser3@example.com",
        "password": "testpassword"
    }
    response = client.post("/auth/login", data=login_payload)
    assert response.status_code == 200
    return response.json()["access_token"]


def test_register_user():
    payload = {
        "email": "testuser3@example.com",
        "password": "testpassword",
        "name": "testuser3"
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code in [200, 400]  # 400 if already registered


def test_login_user():
    login_payload = {
        "username": "testuser3@example.com",
        "password": "testpassword"
    }
    response = client.post("/auth/login", data=login_payload)
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_get_users(user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.get("/users/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_user_by_id(user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    users = client.get("/users/", headers=headers)
    user_id = users.json()[0]["id"]
    response = client.get(f"/users/{user_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == user_id


def test_get_user_by_name(user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.get("/users/name/testuser3", headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "testuser3"


def test_update_user(user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    users = client.get("/users/", headers=headers)
    user_id = users.json()[0]["id"]
    payload = {
        "name": "updateduser",
        "email": "testuser3@example.com",
        "password": "newpassword"
    }
    response = client.put(f"/users/{user_id}", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "updateduser"


def test_create_mood(user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    users = client.get("/users/", headers=headers)
    user_id = users.json()[0]["id"]
    payload = {
        "mood": 5,
        "commentary": "Feeling good today",
        "user_id": user_id
    }
    response = client.post(f"/users/{user_id}/moods/", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["mood"] == 5
    return user_id, response.json()["id"]


def test_get_all_moods_by_user(user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    users = client.get("/users/", headers=headers)
    user_id = users.json()[0]["id"]
    client.post(f"/users/{user_id}/moods/", json={"mood": 5, "commentary": "Test", "user_id": user_id}, headers=headers)
    response = client.get(f"/users/{user_id}/moods/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_mood(user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    users = client.get("/users/", headers=headers)
    user_id = users.json()[0]["id"]
    mood_resp = client.post(f"/users/{user_id}/moods/", json={"mood": 5, "commentary": "Test", "user_id": user_id}, headers=headers)
    mood_id = mood_resp.json()["id"]
    response = client.get(f"/users/{user_id}/moods/{mood_id}/", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == mood_id


def test_update_mood(user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    users = client.get("/users/", headers=headers)
    user_id = users.json()[0]["id"]
    mood_resp = client.post(f"/users/{user_id}/moods/", json={"mood": 5, "commentary": "Test", "user_id": user_id}, headers=headers)
    mood_id = mood_resp.json()["id"]
    payload = {
        "mood": 7,
        "commentary": "Updated mood",
        "user_id": user_id
    }
    response = client.put(f"/users/{user_id}/moods/{mood_id}/", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["mood"] == 7


def test_delete_mood(user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    users = client.get("/users/", headers=headers)
    user_id = users.json()[0]["id"]
    mood_resp = client.post(f"/users/{user_id}/moods/", json={"mood": 5, "commentary": "Test", "user_id": user_id}, headers=headers)
    mood_id = mood_resp.json()["id"]
    response = client.delete(f"/users/{user_id}/moods/{mood_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == mood_id


def test_create_journal(user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    users = client.get("/users/", headers=headers)
    user_id = users.json()[0]["id"]
    mood_resp = client.post(f"/users/{user_id}/moods/", json={"mood": 5, "commentary": "Test", "user_id": user_id}, headers=headers)
    mood_id = mood_resp.json()["id"]
    payload = {
        "title": "My Journal",
        "content": "Today was great!",
        "mood_id": mood_id
    }
    response = client.post(f"/users/{user_id}/moods/{mood_id}/journals/", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["title"] == "My Journal"
    return user_id, mood_id, response.json()["id"]


def test_get_all_journals_by_mood(user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    users = client.get("/users/", headers=headers)
    user_id = users.json()[0]["id"]
    mood_resp = client.post(f"/users/{user_id}/moods/", json={"mood": 5, "commentary": "Test", "user_id": user_id}, headers=headers)
    mood_id = mood_resp.json()["id"]
    client.post(f"/users/{user_id}/moods/{mood_id}/journals/", json={"title": "My Journal", "content": "Today was great!", "mood_id": mood_id}, headers=headers)
    response = client.get(f"/users/{user_id}/moods/{mood_id}/journals/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_journal(user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    users = client.get("/users/", headers=headers)
    user_id = users.json()[0]["id"]
    mood_resp = client.post(f"/users/{user_id}/moods/", json={"mood": 5, "commentary": "Test", "user_id": user_id}, headers=headers)
    mood_id = mood_resp.json()["id"]
    journal_resp = client.post(f"/users/{user_id}/moods/{mood_id}/journals/", json={"title": "My Journal", "content": "Today was great!", "mood_id": mood_id}, headers=headers)
    journal_id = journal_resp.json()["id"]
    response = client.get(f"/users/{user_id}/moods/{mood_id}/journals/{journal_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == journal_id


def test_update_journal(user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    users = client.get("/users/", headers=headers)
    user_id = users.json()[0]["id"]
    mood_resp = client.post(f"/users/{user_id}/moods/", json={"mood": 5, "commentary": "Test", "user_id": user_id}, headers=headers)
    mood_id = mood_resp.json()["id"]
    journal_resp = client.post(f"/users/{user_id}/moods/{mood_id}/journals/", json={"title": "My Journal", "content": "Today was great!", "mood_id": mood_id}, headers=headers)
    journal_id = journal_resp.json()["id"]
    payload = {
        "title": "Updated Journal",
        "content": "Updated content!",
        "mood_id": mood_id
    }
    response = client.put(f"/users/{user_id}/moods/{mood_id}/journals/{journal_id}", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Journal"


def test_delete_journal(user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    users = client.get("/users/", headers=headers)
    user_id = users.json()[0]["id"]
    mood_resp = client.post(f"/users/{user_id}/moods/", json={"mood": 5, "commentary": "Test", "user_id": user_id}, headers=headers)
    mood_id = mood_resp.json()["id"]
    journal_resp = client.post(f"/users/{user_id}/moods/{mood_id}/journals/", json={"title": "My Journal", "content": "Today was great!", "mood_id": mood_id}, headers=headers)
    journal_id = journal_resp.json()["id"]
    response = client.delete(f"/users/{user_id}/moods/{mood_id}/journals/{journal_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == journal_id
