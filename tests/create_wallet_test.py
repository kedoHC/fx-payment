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
        # Create a test user with unique email
        test_user = UsersModel(
            email="auth@example.com",
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
        yield

def test_create_wallet_success_default_balance(client, auth_headers):
    """Test wallet creation service returns 201 with default balance"""
    # First, create a user
    user_payload = {
        "email": "test@example.com",
        "password": "password123"
    }
    user_response = client.post('/users', json=user_payload)
    assert user_response.status_code == 201
    
    # Get the user from database to get the auto-generated ID
    user = UsersModel.query.filter_by(email="test@example.com").first()
    user_id = user.id  # Integer as expected by schema and model
    
    # Now create wallet for this user
    wallet_payload = {
        "user_id": user_id
    }
    response = client.post('/wallets', json=wallet_payload, headers=auth_headers)
    assert response.status_code == 201
    response_data = json.loads(response.data)
    assert response_data["message"] == "Wallet created successfully"
    assert response_data["user_id"] == user_id
    assert "wallet_id" in response_data
    
    # Verify wallet was created in database
    wallet = WalletsModel.query.filter_by(user_id=user_id).first()  # Now both are integers
    assert wallet is not None
    assert wallet.balance == 0.0
    assert wallet.currency == "MXN"
    assert wallet.recent_transactions == 0

def test_create_wallet_with_mxn_initial_balance(client, auth_headers):
    """Test wallet creation with MXN initial balance"""
    # Create a user first
    user_payload = {
        "email": "test2@example.com",
        "password": "password123"
    }
    user_response = client.post('/users', json=user_payload)
    assert user_response.status_code == 201
    
    # Get the user from database
    user = UsersModel.query.filter_by(email="test2@example.com").first()
    user_id = user.id  # Integer as expected by schema and model
    
    # Create wallet with MXN balance
    wallet_payload = {
        "user_id": user_id,
        "initial_balance": 1000.0,
        "currency": "MXN"
    }
    response = client.post('/wallets', json=wallet_payload, headers=auth_headers)
    assert response.status_code == 201
    
    # Verify wallet has correct MXN balance
    wallet = WalletsModel.query.filter_by(user_id=user_id).first()  # Now both are integers
    assert wallet is not None
    assert wallet.balance == 1000.0
    assert wallet.currency == "MXN"

def test_create_wallet_with_usd_initial_balance(client, auth_headers):
    """Test wallet creation with USD initial balance (converted to MXN)"""
    # Create a user first
    user_payload = {
        "email": "test3@example.com",
        "password": "password123"
    }
    user_response = client.post('/users', json=user_payload)
    assert user_response.status_code == 201
    
    # Get the user from database
    user = UsersModel.query.filter_by(email="test3@example.com").first()
    user_id = user.id  # Integer as expected by schema and model
    
    # Create wallet with USD balance
    wallet_payload = {
        "user_id": user_id,
        "initial_balance": 100.0,
        "currency": "USD"
    }
    response = client.post('/wallets', json=wallet_payload, headers=auth_headers)
    assert response.status_code == 201
    
    # Verify wallet has converted USD to MXN (100 USD * 18.7 = 1870 MXN)
    wallet = WalletsModel.query.filter_by(user_id=user_id).first()  # Now both are integers
    assert wallet is not None
    assert wallet.balance == 1870.0  # 100 * 18.7
    assert wallet.currency == "MXN"

def test_create_wallet_user_not_found(client, auth_headers):
    """Test wallet creation for non-existent user returns 404"""
    wallet_payload = {
        "user_id": 999  # Non-existent user ID as integer
    }
    response = client.post('/wallets', json=wallet_payload, headers=auth_headers)
    assert response.status_code == 404
    response_data = json.loads(response.data)
    assert "The provided user is not registered" in response_data["error"]

def test_create_wallet_duplicate_wallet(client, auth_headers):
    """Test creating duplicate wallet for user returns 409"""
    # Create a user first
    user_payload = {
        "email": "test4@example.com",
        "password": "password123"
    }
    user_response = client.post('/users', json=user_payload)
    assert user_response.status_code == 201
    
    # Get the user from database
    user = UsersModel.query.filter_by(email="test4@example.com").first()
    user_id = user.id  # Integer as expected by schema and model
    
    # Create first wallet
    wallet_payload = {
        "user_id": user_id
    }
    response1 = client.post('/wallets', json=wallet_payload, headers=auth_headers)
    assert response1.status_code == 201
    
    # Try to create second wallet for same user
    response2 = client.post('/wallets', json=wallet_payload, headers=auth_headers)
    assert response2.status_code == 409
    response_data = json.loads(response2.data)
    assert "Wallet already exists for this user" in response_data["error"]

def test_create_wallet_missing_user_id(client, auth_headers):
    """Test wallet creation without user_id returns 422"""
    wallet_payload = {
        "initial_balance": 100.0
        # Missing user_id
    }
    response = client.post('/wallets', json=wallet_payload, headers=auth_headers)
    assert response.status_code == 422
    response_data = json.loads(response.data)
    assert "errors" in response_data
    assert "user_id" in response_data["errors"]

def test_create_wallet_invalid_balance(client, auth_headers):
    """Test wallet creation with negative balance returns 422"""
    # Create a user first
    user_payload = {
        "email": "test5@example.com",
        "password": "password123"
    }
    user_response = client.post('/users', json=user_payload)
    assert user_response.status_code == 201
    
    # Get the user from database
    user = UsersModel.query.filter_by(email="test5@example.com").first()
    user_id = user.id  # Integer as expected by schema and model
    
    wallet_payload = {
        "user_id": user_id,
        "initial_balance": -100.0  # Invalid negative balance
    }
    response = client.post('/wallets', json=wallet_payload, headers=auth_headers)
    assert response.status_code == 422
    response_data = json.loads(response.data)
    assert "errors" in response_data
    assert "initial_balance" in response_data["errors"]

def test_create_wallet_no_json_data(client, auth_headers):
    """Test wallet creation with no JSON data returns 400"""
    response = client.post('/wallets', data='', content_type="application/json", headers=auth_headers)
    assert response.status_code == 400
    # The endpoint uses abort() which returns HTML, not JSON
    assert "400 Bad Request" in response.data.decode('utf-8')

def test_create_wallet_malformed_json(client, auth_headers):
    """Test wallet creation with malformed JSON returns 400"""
    response = client.post('/wallets', 
                          data='{invalid json}',
                          content_type="application/json",
                          headers=auth_headers)
    assert response.status_code == 400
    # The endpoint uses abort() which returns HTML, not JSON
    assert "400 Bad Request" in response.data.decode('utf-8')

def test_create_wallet_unauthorized(client):
    """Test that endpoint requires authentication"""
    wallet_payload = {
        "user_id": 1
    }
    response = client.post('/wallets', json=wallet_payload)
    assert response.status_code == 401
    response_data = json.loads(response.data)
    assert "error" in response_data

def test_create_wallet_integer_id_generation(client, auth_headers):
    """Test that wallet IDs are generated as integers"""
    # Create a user first
    user_payload = {
        "email": "integer@example.com",
        "password": "password123"
    }
    user_response = client.post('/users', json=user_payload)
    assert user_response.status_code == 201
    
    # Get the user from database
    user = UsersModel.query.filter_by(email="integer@example.com").first()
    user_id = user.id  # Integer as expected by schema and model
    
    # Create wallet
    wallet_payload = {
        "user_id": user_id
    }
    response = client.post('/wallets', json=wallet_payload, headers=auth_headers)
    assert response.status_code == 201
    response_data = json.loads(response.data)
    
    # Verify wallet_id is an integer
    wallet_id = response_data["wallet_id"]
    assert isinstance(wallet_id, int)
    assert wallet_id > 0  # Should be a positive integer
    
    # Verify wallet exists in database with this integer ID
    wallet = WalletsModel.query.filter_by(id=wallet_id).first()
    assert wallet is not None
    assert wallet.user_id == user_id  # Now both are integers, no conversion needed