import pytest
import os
import sys
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from db import db
from models import UsersModel, WalletsModel
from flask_jwt_extended import create_access_token
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

@pytest.fixture
def auth_headers(app):
    """Create JWT token for authentication."""
    with app.app_context():
        # Create a test user
        test_user = UsersModel(
            email="test@example.com",
            password=pbkdf2_sha256.hash("testpassword")
        )
        db.session.add(test_user)
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(identity=str(test_user.id))
        return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture(autouse=True)
def setup_test_data(app):
    """Set up test data in the database for each test."""
    with app.app_context():
        # Clear existing data
        db.session.query(WalletsModel).delete()
        db.session.query(UsersModel).delete()
        db.session.commit()
        
        # Create test user for conversion tests
        test_user = UsersModel(
            email="diana@example.com",
            password=pbkdf2_sha256.hash("password123"),
            is_active=True
        )
        db.session.add(test_user)
        db.session.commit()
        
        # Store the user ID for use in tests
        app.test_user_id = test_user.id
        yield

def test_convert_currency_success(client, auth_headers, app):
    """Test convert service returns 200 with correct conversion"""
    payload = {
        "from_currency": "USD",
        "to_currency": "MXN",
        "amount": 100.0
    }
    user_id = app.test_user_id
    response = client.post(f'/wallets/{user_id}/convert', json=payload, headers=auth_headers)
    
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert "amount" in response_data
    # 100 USD * 18.70 = 1870 MXN
    assert response_data["amount"] == 1870.0

def test_convert_currency_user_not_found(client, auth_headers):
    """Return 404 when the user doesn't exist"""
    payload = {
        "from_currency": "MXN",
        "to_currency": "USD", 
        "amount": 1870.0
    }
    response = client.post("/wallets/999/convert", json=payload, headers=auth_headers)
    assert response.status_code == 404
    # The endpoint uses abort() which returns HTML, not JSON
    assert "404 Not Found" in response.data.decode('utf-8')

def test_convert_currency_invalid_json(client, auth_headers, app):
    """Return 422 when JSON body fails validation"""
    # Missing required field 'amount'
    payload = {
        "from_currency": "USD",
        "to_currency": "MXN"
    }
    user_id = app.test_user_id
    response = client.post(f"/wallets/{user_id}/convert", json=payload, headers=auth_headers)
    
    assert response.status_code == 422
    response_data = json.loads(response.data)
    assert "errors" in response_data

def test_convert_currency_malformed_json(client, auth_headers, app):
    """Return 400 when JSON data is malformed"""
    user_id = app.test_user_id
    response = client.post(
        f"/wallets/{user_id}/convert",
        data='{invalid json}',
        content_type="application/json",
        headers=auth_headers
    )
    assert response.status_code == 400
    # The endpoint uses abort() which returns HTML, not JSON
    assert "400 Bad Request" in response.data.decode('utf-8')

def test_convert_currency_unauthorized(client, app):
    """Test that endpoint requires authentication"""
    payload = {
        "from_currency": "USD",
        "to_currency": "MXN",
        "amount": 100.0
    }
    user_id = app.test_user_id
    response = client.post(f'/wallets/{user_id}/convert', json=payload)
    assert response.status_code == 401
    response_data = json.loads(response.data)
    assert "error" in response_data

def test_convert_currency_inactive_user(client, auth_headers, app):
    """Test conversion with inactive user returns 404"""
    # Create an inactive user
    inactive_user = UsersModel(
        email="inactive@example.com",
        password=pbkdf2_sha256.hash("password123"),
        is_active=False
    )
    db.session.add(inactive_user)
    db.session.commit()
    
    payload = {
        "from_currency": "USD",
        "to_currency": "MXN",
        "amount": 100.0
    }
    response = client.post(f'/wallets/{inactive_user.id}/convert', json=payload, headers=auth_headers)
    
    assert response.status_code == 404
    # The endpoint uses abort() which returns HTML, not JSON
    assert "404 Not Found" in response.data.decode('utf-8')

def test_convert_currency_reverse_conversion(client, auth_headers, app):
    """Test MXN to USD conversion"""
    payload = {
        "from_currency": "MXN",
        "to_currency": "USD",
        "amount": 1870.0
    }
    user_id = app.test_user_id
    response = client.post(f'/wallets/{user_id}/convert', json=payload, headers=auth_headers)
    
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert "amount" in response_data
    # 1870 MXN / 18.70 = 100 USD
    assert response_data["amount"] == 100.0
