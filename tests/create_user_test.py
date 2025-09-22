import pytest
import os
import sys
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from store.users import users_data

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture(autouse=True)
def cleanup_data():
    # Save original data
    original_users = users_data.copy()
    yield
    # Restore original data
    users_data.clear()
    users_data.extend(original_users)


def test_create_user_success(client):
    """ Test user creation service returns 201 """
    payload = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "age": 30,
        "is_active": True
    }
    response = client.post('/users', json=payload)
    assert response.status_code == 201
    response_data = json.loads(response.data)
    assert response_data["message"] == "User created successfully"
    assert "user_id" in response_data
    
    # Verify user was added to users_data
    new_user = next((user for user in users_data if user["email"] == "john.doe@example.com"), None)
    assert new_user is not None
    assert new_user["name"] == "John Doe"
    assert new_user["age"] == 30
    assert new_user["is_active"] == True


def test_create_user_default_active_status(client):
    """ Test user creation with default is_active=True """
    payload = {
        "name": "Jane Smith",
        "email": "jane.smith@example.com",
        "age": 25
    }
    response = client.post('/users', json=payload)
    assert response.status_code == 201
    
    # Verify user has default is_active=True
    new_user = next((user for user in users_data if user["email"] == "jane.smith@example.com"), None)
    assert new_user is not None
    assert new_user["is_active"] == True


def test_create_user_duplicate_email(client):
    """ Test creating user with existing email returns 409 """
    # First user
    payload1 = {
        "name": "First User",
        "email": "duplicate@example.com",
        "age": 30
    }
    response1 = client.post('/users', json=payload1)
    assert response1.status_code == 201
    
    # Second user with same email
    payload2 = {
        "name": "Second User",
        "email": "duplicate@example.com",
        "age": 25
    }
    response2 = client.post('/users', json=payload2)
    assert response2.status_code == 409
    response_data = json.loads(response2.data)
    assert "User with this email already exists" in response_data["error"]


def test_create_user_invalid_json(client):
    """ Test creation with invalid JSON returns 422 """
    payload = {
        "name": "John Doe",
        "email": "invalid-email",  # Invalid email format
        "age": 30
    }
    response = client.post('/users', json=payload)
    assert response.status_code == 422
    response_data = json.loads(response.data)
    assert "errors" in response_data


def test_create_user_missing_required_fields(client):
    """ Test creation with missing required fields returns 422 """
    payload = {
        "name": "John Doe"
        # Missing email and age
    }
    response = client.post('/users', json=payload)
    assert response.status_code == 422
    response_data = json.loads(response.data)
    assert "errors" in response_data
    assert "email" in response_data["errors"]
    assert "age" in response_data["errors"]


def test_create_user_invalid_age(client):
    """ Test creation with invalid age returns 422 """
    payload = {
        "name": "John Doe",
        "email": "john@example.com",
        "age": -5  # Invalid negative age
    }
    response = client.post('/users', json=payload)
    assert response.status_code == 422
    response_data = json.loads(response.data)
    assert "errors" in response_data
    assert "age" in response_data["errors"]


def test_create_user_no_json_data(client):
    """ Test creation with no JSON data returns 400 """
    response = client.post('/users', data='', content_type="application/json")
    assert response.status_code == 400
    assert "400 Bad Request" in response.data.decode('utf-8')


def test_create_user_malformed_json(client):
    """ Test creation with malformed JSON returns 400 """
    response = client.post('/users', 
                          data='{invalid json}',
                          content_type="application/json")
    assert response.status_code == 400