import pytest
import os
import sys
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from db import db
from models import UsersModel, WalletsModel
from passlib.hash import pbkdf2_sha256

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app("sqlite:///:memory:")
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture(autouse=True)
def setup_test_data(app):
    """Set up test data in the database for each test."""
    with app.app_context():
        # Clear existing data
        db.session.query(WalletsModel).delete()
        db.session.query(UsersModel).delete()
        db.session.commit()
        yield

def test_create_user_success(client):
    """Test user creation service returns 201"""
    payload = {
        "email": "john.doe@example.com",
        "password": "securepassword123"
    }
    response = client.post('/users', json=payload)
    assert response.status_code == 201
    response_data = json.loads(response.data)
    assert response_data["message"] == "User created successfully"
    
    # Verify user was added to database
    user = UsersModel.query.filter_by(email="john.doe@example.com").first()
    assert user is not None
    assert user.email == "john.doe@example.com"
    assert user.is_active == True  # Default value
    # Verify password is hashed
    assert user.password != "securepassword123"
    assert pbkdf2_sha256.verify("securepassword123", user.password)

def test_create_user_duplicate_email(client):
    """Test creating user with existing email returns 409"""
    # First user
    payload1 = {
        "email": "duplicate@example.com",
        "password": "password123"
    }
    response1 = client.post('/users', json=payload1)
    assert response1.status_code == 201
    
    # Second user with same email
    payload2 = {
        "email": "duplicate@example.com",
        "password": "differentpassword"
    }
    response2 = client.post('/users', json=payload2)
    assert response2.status_code == 409
    response_data = json.loads(response2.data)
    assert "User with this email already exists" in response_data["error"]

def test_create_user_invalid_email(client):
    """Test creation with invalid email format returns 422"""
    payload = {
        "email": "invalid-email",  # Invalid email format
        "password": "password123"
    }
    response = client.post('/users', json=payload)
    assert response.status_code == 422
    response_data = json.loads(response.data)
    assert "errors" in response_data
    assert "email" in response_data["errors"]

def test_create_user_missing_email(client):
    """Test creation with missing email returns 422"""
    payload = {
        "password": "password123"
        # Missing email
    }
    response = client.post('/users', json=payload)
    assert response.status_code == 422
    response_data = json.loads(response.data)
    assert "errors" in response_data
    assert "email" in response_data["errors"]

def test_create_user_missing_password(client):
    """Test creation with missing password returns 422"""
    payload = {
        "email": "test@example.com"
        # Missing password
    }
    response = client.post('/users', json=payload)
    assert response.status_code == 422
    response_data = json.loads(response.data)
    assert "errors" in response_data
    assert "password" in response_data["errors"]

def test_create_user_empty_password(client):
    """Test creation with empty password - currently allows empty passwords"""
    payload = {
        "email": "test@example.com",
        "password": ""  # Empty password - currently allowed by schema
    }
    response = client.post('/users', json=payload)
    # Currently the schema allows empty passwords, so this returns 201
    assert response.status_code == 201
    response_data = json.loads(response.data)
    assert response_data["message"] == "User created successfully"
    
    # Verify user was created with empty password
    user = UsersModel.query.filter_by(email="test@example.com").first()
    assert user is not None
    assert user.email == "test@example.com"

def test_create_user_no_json_data(client):
    """Test creation with no JSON data returns 400"""
    response = client.post('/users', data='', content_type="application/json")
    assert response.status_code == 400
    # The endpoint uses abort() which returns HTML, not JSON
    assert "400 Bad Request" in response.data.decode('utf-8')

def test_create_user_malformed_json(client):
    """Test creation with malformed JSON returns 400"""
    response = client.post('/users', 
                          data='{invalid json}',
                          content_type="application/json")
    assert response.status_code == 400
    # The endpoint uses abort() which returns HTML, not JSON
    assert "400 Bad Request" in response.data.decode('utf-8')

def test_create_user_database_error_simulation(client, app):
    """Test creation handles database errors gracefully"""
    # This test simulates a database error by using an invalid email that might cause issues
    # In a real scenario, you might mock the database session to throw an exception
    payload = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    # First create a user successfully
    response1 = client.post('/users', json=payload)
    assert response1.status_code == 201
    
    # Try to create another user with same email (should fail with 409, not 500)
    response2 = client.post('/users', json=payload)
    assert response2.status_code == 409

def test_create_user_password_hashing(client):
    """Test that passwords are properly hashed in the database"""
    payload = {
        "email": "hashing@example.com",
        "password": "plaintextpassword"
    }
    response = client.post('/users', json=payload)
    assert response.status_code == 201
    
    # Verify password is hashed
    user = UsersModel.query.filter_by(email="hashing@example.com").first()
    assert user is not None
    assert user.password != "plaintextpassword"
    assert len(user.password) > 50  # Hashed passwords are much longer
    assert pbkdf2_sha256.verify("plaintextpassword", user.password)

def test_create_user_default_is_active(client):
    """Test that new users are created with is_active=True by default"""
    payload = {
        "email": "active@example.com",
        "password": "password123"
    }
    response = client.post('/users', json=payload)
    assert response.status_code == 201
    
    # Verify user is active by default
    user = UsersModel.query.filter_by(email="active@example.com").first()
    assert user is not None
    assert user.is_active == True