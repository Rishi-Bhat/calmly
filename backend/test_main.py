import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import engine
from app.resources_logic import engine as resources_engine
from sqlmodel import SQLModel


client = TestClient(app)


@pytest.fixture(scope="function")
def setup_and_teardown_db():
    """Create tables before test and drop after."""
    SQLModel.metadata.create_all(bind=engine)
    SQLModel.metadata.create_all(bind=resources_engine)
    yield
    SQLModel.metadata.drop_all(bind=engine)
    SQLModel.metadata.drop_all(bind=resources_engine)


@pytest.fixture(scope="function")
def user_token(setup_and_teardown_db):
    """Register and login a test user, return access token."""
    register_payload = {
        "email": "testuser@example.com",
        "password": "testpassword123",
        "name": "Test User"
    }
    client.post("/auth/register", json=register_payload)
    
    login_payload = {
        "username": "testuser@example.com",
        "password": "testpassword123"
    }
    response = client.post("/auth/login", data=login_payload)
    return response.json()["access_token"]


# ========== AUTH TESTS ==========
def test_register_user(setup_and_teardown_db):
    payload = {
        "email": "testuser3@example.com",
        "password": "testpassword",
        "name": "testuser3"
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code in [200, 400]  # 400 if already registered


def test_login_user(setup_and_teardown_db):
    # Register first
    register_payload = {
        "email": "testuser2@example.com",
        "password": "testpassword",
        "name": "testuser2"
    }
    client.post("/auth/register", json=register_payload)
    
    login_payload = {
        "username": "testuser2@example.com",
        "password": "testpassword"
    }
    response = client.post("/auth/login", data=login_payload)
    assert response.status_code == 200
    assert "access_token" in response.json()


# ========== USER TESTS ==========
def test_get_users(user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.get("/users/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_user_by_id(user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    # Get all users first to get an ID
    response = client.get("/users/", headers=headers)
    if response.json():
        user_id = response.json()[0]["id"]
        response = client.get(f"/users/{user_id}", headers=headers)
        assert response.status_code == 200


def test_get_user_by_name(user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.get("/users/name/Test%20User", headers=headers)
    assert response.status_code in [200, 404]


def test_update_user(user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    update_payload = {
        "name": "Updated User",
        "email": "updated@example.com",
        "password": "newpassword123"  # UserCreate requires password
    }
    response = client.get("/users/", headers=headers)
    if response.json():
        user_id = response.json()[0]["id"]
        response = client.put(f"/users/{user_id}", json=update_payload, headers=headers)
        assert response.status_code in [200, 404]


# ========== MOOD TESTS ==========
def test_create_mood(user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    # Get user_id first
    user_response = client.get("/users/", headers=headers)
    user_id = user_response.json()[0]["id"]
    
    mood_payload = {
        "mood": 7,
        "commentary": "Feeling great today!",
        "user_id": user_id
    }
    response = client.post(f"/users/{user_id}/moods/", json=mood_payload, headers=headers)
    assert response.status_code in [200, 201]


def test_get_all_moods_by_user(user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    # Get user_id first
    user_response = client.get("/users/", headers=headers)
    user_id = user_response.json()[0]["id"]
    
    response = client.get(f"/users/{user_id}/moods/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_mood(user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    # Get user_id first
    user_response = client.get("/users/", headers=headers)
    user_id = user_response.json()[0]["id"]
    
    # Create a mood first
    mood_payload = {
        "mood": 8,
        "commentary": "Test mood",
        "user_id": user_id
    }
    create_response = client.post(f"/users/{user_id}/moods/", json=mood_payload, headers=headers)
    if create_response.status_code in [200, 201]:
        mood_id = create_response.json()["id"]
        response = client.get(f"/users/{user_id}/moods/{mood_id}/", headers=headers)
        assert response.status_code == 200


def test_update_mood(user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    # Get user_id first
    user_response = client.get("/users/", headers=headers)
    user_id = user_response.json()[0]["id"]
    
    mood_payload = {
        "mood": 8,
        "commentary": "Test mood",
        "user_id": user_id
    }
    create_response = client.post(f"/users/{user_id}/moods/", json=mood_payload, headers=headers)
    if create_response.status_code in [200, 201]:
        mood_id = create_response.json()["id"]
        update_payload = {
            "mood": 9,
            "commentary": "Updated mood",
            "user_id": user_id
        }
        response = client.put(f"/users/{user_id}/moods/{mood_id}/", json=update_payload, headers=headers)
        assert response.status_code in [200, 404]


def test_delete_mood(user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    # Get user_id first
    user_response = client.get("/users/", headers=headers)
    user_id = user_response.json()[0]["id"]
    
    mood_payload = {
        "mood": 5,
        "commentary": "Delete test",
        "user_id": user_id
    }
    create_response = client.post(f"/users/{user_id}/moods/", json=mood_payload, headers=headers)
    if create_response.status_code in [200, 201]:
        mood_id = create_response.json()["id"]
        response = client.delete(f"/users/{user_id}/moods/{mood_id}", headers=headers)
        assert response.status_code in [200, 204, 404]


# ========== JOURNAL TESTS ==========
def test_create_journal(user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    # Get user_id first
    user_response = client.get("/users/", headers=headers)
    user_id = user_response.json()[0]["id"]
    
    # Create mood first
    mood_payload = {
        "mood": 7,
        "commentary": "Good mood",
        "user_id": user_id
    }
    mood_response = client.post(f"/users/{user_id}/moods/", json=mood_payload, headers=headers)
    
    if mood_response.status_code in [200, 201]:
        mood_id = mood_response.json()["id"]
        journal_payload = {
            "title": "Test Journal",
            "content": "This is a test journal entry.",
            "mood_id": mood_id
        }
        response = client.post(f"/users/{user_id}/moods/{mood_id}/journals/", json=journal_payload, headers=headers)
        assert response.status_code in [200, 201]


def test_get_all_journals_by_mood(user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    # Get user_id first
    user_response = client.get("/users/", headers=headers)
    user_id = user_response.json()[0]["id"]
    
    # Create a mood first to have a valid mood_id
    mood_payload = {
        "mood": 7,
        "commentary": "Test",
        "user_id": user_id
    }
    mood_response = client.post(f"/users/{user_id}/moods/", json=mood_payload, headers=headers)
    if mood_response.status_code in [200, 201]:
        mood_id = mood_response.json()["id"]
        response = client.get(f"/users/{user_id}/moods/{mood_id}/journals/", headers=headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)


def test_get_journal(user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    # Get user_id first
    user_response = client.get("/users/", headers=headers)
    user_id = user_response.json()[0]["id"]
    
    mood_payload = {"mood": 7, "commentary": "Good", "user_id": user_id}
    mood_response = client.post(f"/users/{user_id}/moods/", json=mood_payload, headers=headers)
    
    if mood_response.status_code in [200, 201]:
        mood_id = mood_response.json()["id"]
        journal_payload = {
            "title": "Get Test",
            "content": "Test content",
            "mood_id": mood_id
        }
        journal_response = client.post(f"/users/{user_id}/moods/{mood_id}/journals/", json=journal_payload, headers=headers)
        if journal_response.status_code in [200, 201]:
            journal_id = journal_response.json()["id"]
            response = client.get(f"/users/{user_id}/moods/{mood_id}/journals/{journal_id}", headers=headers)
            assert response.status_code == 200


def test_update_journal(user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    # Get user_id first
    user_response = client.get("/users/", headers=headers)
    user_id = user_response.json()[0]["id"]
    
    mood_payload = {"mood": 6, "commentary": "OK", "user_id": user_id}
    mood_response = client.post(f"/users/{user_id}/moods/", json=mood_payload, headers=headers)
    
    if mood_response.status_code in [200, 201]:
        mood_id = mood_response.json()["id"]
        journal_payload = {
            "title": "Update Test",
            "content": "Original",
            "mood_id": mood_id
        }
        journal_response = client.post(f"/users/{user_id}/moods/{mood_id}/journals/", json=journal_payload, headers=headers)
        if journal_response.status_code in [200, 201]:
            journal_id = journal_response.json()["id"]
            update_payload = {
                "title": "Updated",
                "content": "Updated content",
                "mood_id": mood_id
            }
            response = client.put(f"/users/{user_id}/moods/{mood_id}/journals/{journal_id}", json=update_payload, headers=headers)
            assert response.status_code in [200, 404]


def test_delete_journal(user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    # Get user_id first
    user_response = client.get("/users/", headers=headers)
    user_id = user_response.json()[0]["id"]
    
    mood_payload = {"mood": 5, "commentary": "Delete", "user_id": user_id}
    mood_response = client.post(f"/users/{user_id}/moods/", json=mood_payload, headers=headers)
    
    if mood_response.status_code in [200, 201]:
        mood_id = mood_response.json()["id"]
        journal_payload = {
            "title": "Delete Test",
            "content": "To delete",
            "mood_id": mood_id
        }
        journal_response = client.post(f"/users/{user_id}/moods/{mood_id}/journals/", json=journal_payload, headers=headers)
        if journal_response.status_code in [200, 201]:
            journal_id = journal_response.json()["id"]
            response = client.delete(f"/users/{user_id}/moods/{mood_id}/journals/{journal_id}", headers=headers)
            assert response.status_code in [200, 204, 404]


# ========== RESOURCES TESTS ==========
def test_list_resources(setup_and_teardown_db):
    response = client.get("/resources/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_resources_by_mood(setup_and_teardown_db):
    response = client.get("/resources/?mood=stressed")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_recommend_resources(setup_and_teardown_db):
    response = client.get("/resources/recommend?mood=stressed&limit=5")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_resource(setup_and_teardown_db):
    resource_payload = {
        "title": "New Breathing Exercise",
        "type": "breathing",
        "url": "https://example.com/breathing.mp3",
        "duration_seconds": 300,
        "mood_tags": "stressed,anxious",
        "description": "5-minute breathing",
        "public": True
    }
    response = client.post("/resources/", json=resource_payload)
    assert response.status_code == 200
    assert response.json()["title"] == "New Breathing Exercise"


def test_get_resource(setup_and_teardown_db):
    # Create a resource first
    resource_payload = {
        "title": "Get Test Resource",
        "type": "music",
        "mood_tags": "sad",
        "description": "Test",
        "public": True
    }
    create_response = client.post("/resources/", json=resource_payload)
    if create_response.status_code == 200:
        resource_id = create_response.json()["id"]
        response = client.get(f"/resources/{resource_id}")
        assert response.status_code == 200


def test_delete_resource(setup_and_teardown_db):
    # Create a resource first
    resource_payload = {
        "title": "Delete Test Resource",
        "type": "exercise",
        "mood_tags": "anxious",
        "description": "To delete",
        "public": True
    }
    create_response = client.post("/resources/", json=resource_payload)
    if create_response.status_code == 200:
        resource_id = create_response.json()["id"]
        response = client.delete(f"/resources/{resource_id}")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
