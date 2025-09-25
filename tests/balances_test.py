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
        
        # Create test users and wallets - let the DB generate IDs
        # User 1: Diana with high balance (1870 MXN = 100 USD)
        user1 = UsersModel(
            email="diana@example.com",
            password=pbkdf2_sha256.hash("password123")
        )
        db.session.add(user1)
        db.session.flush()  # Get the auto-generated user ID
        
        wallet1 = WalletsModel(
            user_id=user1.id,  # Use the auto-generated ID
            balance=1870.0,
            currency="MXN",
            recent_transactions=35
        )
        db.session.add(wallet1)
        
        # User 2: Bob with moderate balance (935 MXN = 50 USD)
        user2 = UsersModel(
            email="bob@example.com",
            password=pbkdf2_sha256.hash("password123")
        )
        db.session.add(user2)
        db.session.flush()
        
        wallet2 = WalletsModel(
            user_id=user2.id,  # Use the auto-generated ID
            balance=935.0,
            currency="MXN",
            recent_transactions=12
        )
        db.session.add(wallet2)
        
        # User 3: Charlie with zero balance
        user3 = UsersModel(
            email="charlie@example.com",
            password=pbkdf2_sha256.hash("password123")
        )
        db.session.add(user3)
        db.session.flush()
        
        wallet3 = WalletsModel(
            user_id=user3.id,  # Use the auto-generated ID
            balance=0.0,
            currency="MXN",
            recent_transactions=0
        )
        db.session.add(wallet3)
        
        db.session.commit()
        
        # Store the user IDs for use in tests
        app.test_user_ids = {
            'diana': user1.id,
            'bob': user2.id,
            'charlie': user3.id
        }
        yield

def test_get_balances_success(client, auth_headers, app):
    """Test get balances service returns 200 with correct balances"""
    # Use Diana's auto-generated user ID with 1870 MXN (100 USD)
    user_id = app.test_user_ids['diana']
    response = client.get(f'/wallets/{user_id}/balances', headers=auth_headers)
    
    assert response.status_code == 200
    response_data = json.loads(response.data)
    
    # Check that both currencies are returned
    assert "mxn" in response_data
    assert "usd" in response_data
    
    # Check correct values: 1870 MXN = 100 USD (1870 / 18.70)
    assert response_data["mxn"] == 1870.0
    assert response_data["usd"] == 100.0

def test_get_balances_user_not_found(client, auth_headers):
    """Return 404 when the user doesn't exist"""
    response = client.get("/wallets/999/balances", headers=auth_headers)
    assert response.status_code == 404
    response_data = json.loads(response.data)
    assert "error" in response_data
    assert "User not found" in response_data["error"]

def test_get_balances_zero_balance(client, auth_headers, app):
    """Test get balances with zero balance"""
    # Use Charlie's auto-generated user ID with 0 MXN
    user_id = app.test_user_ids['charlie']
    response = client.get(f'/wallets/{user_id}/balances', headers=auth_headers)
    
    assert response.status_code == 200
    response_data = json.loads(response.data)
    
    # Check that both currencies show zero
    assert response_data["mxn"] == 0.0
    assert response_data["usd"] == 0.0

def test_get_balances_moderate_balance(client, auth_headers, app):
    """Test get balances with moderate balance"""
    # Use Bob's auto-generated user ID with 935 MXN (50 USD)
    user_id = app.test_user_ids['bob']
    response = client.get(f'/wallets/{user_id}/balances', headers=auth_headers)
    
    assert response.status_code == 200
    response_data = json.loads(response.data)
    
    # Check correct values: 935 MXN = 50 USD (935 / 18.70)
    assert response_data["mxn"] == 935.0
    assert response_data["usd"] == 50.0

def test_get_balances_unauthorized(client):
    """Test that endpoint requires authentication"""
    response = client.get("/wallets/1/balances")
    assert response.status_code == 401
    response_data = json.loads(response.data)
    assert "error" in response_data

def test_get_balances_user_without_wallet(client, auth_headers, app):
    """Test get balances for user without wallet returns 500"""
    # Create a user without wallet
    user_without_wallet = UsersModel(
        email="nowallet@example.com",
        password=pbkdf2_sha256.hash("password123")
    )
    db.session.add(user_without_wallet)
    db.session.commit()
    
    response = client.get(f'/wallets/{user_without_wallet.id}/balances', headers=auth_headers)
    # This should return 500 because user.wallet will be None
    assert response.status_code == 500
    response_data = json.loads(response.data)
    assert "error" in response_data
    assert "Failed to get balances" in response_data["error"]