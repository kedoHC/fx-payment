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
        
        # Create test users and wallets
        # User 1: Diana with sufficient balance (4500.50 MXN)
        user1 = UsersModel(
            email="diana@example.com",
            password=pbkdf2_sha256.hash("password123")
        )
        db.session.add(user1)
        db.session.flush()
        
        wallet1 = WalletsModel(
            user_id=user1.id,
            balance=4500.50,
            currency="MXN",
            recent_transactions=35
        )
        db.session.add(wallet1)
        
        # User 2: Charlie with zero balance
        user2 = UsersModel(
            email="charlie@example.com",
            password=pbkdf2_sha256.hash("password123")
        )
        db.session.add(user2)
        db.session.flush()
        
        wallet2 = WalletsModel(
            user_id=user2.id,
            balance=0.00,
            currency="MXN",
            recent_transactions=0
        )
        db.session.add(wallet2)
        
        db.session.commit()
        
        # Store the wallet IDs for use in tests
        app.test_wallet_ids = {
            'diana': wallet1.id,
            'charlie': wallet2.id
        }
        yield

def test_withdraw_wallet_success(client, auth_headers, app):
    """Test withdraw service returns 200 with successful withdrawal"""
    payload = {
        "currency": "MXN",
        "amount": 100.0
    }
    # Use Diana's wallet with sufficient balance (4500.50 MXN)
    wallet_id = app.test_wallet_ids['diana']
    response = client.post(f'/wallets/{wallet_id}/withdraw', json=payload, headers=auth_headers)
    
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert response_data["message"] == "amount successfully subtracted"
    
    # Check that balance was actually reduced: 4500.50 - 100.0 = 4400.50
    wallet = WalletsModel.query.filter_by(id=wallet_id).first()
    assert wallet.balance == 4400.50

def test_withdraw_wallet_usd_currency(client, auth_headers, app):
    """Test withdraw service with USD currency (converted to MXN)"""
    payload = {
        "currency": "USD",
        "amount": 50.0  # 50 USD = 935 MXN
    }
    wallet_id = app.test_wallet_ids['diana']
    response = client.post(f'/wallets/{wallet_id}/withdraw', json=payload, headers=auth_headers)
    
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert response_data["message"] == "amount successfully subtracted"
    
    # Check that balance was reduced: 4500.50 - 935.0 = 3565.50
    wallet = WalletsModel.query.filter_by(id=wallet_id).first()
    assert wallet.balance == 3565.50

def test_withdraw_wallet_insufficient_balance(client, auth_headers, app):
    """Return operation not allowed when user has insufficient balance"""
    payload = {
        "currency": "MXN",
        "amount": 1000.0  # More than Charlie's balance of 0.00
    }
    wallet_id = app.test_wallet_ids['charlie']
    response = client.post(f"/wallets/{wallet_id}/withdraw", json=payload, headers=auth_headers)
    
    assert response.status_code == 200  # The endpoint returns 200 with "Operation not allowed"
    response_data = json.loads(response.data)
    assert response_data["message"] == "Operation not allowed"
    
    # Check that balance wasn't changed
    wallet = WalletsModel.query.filter_by(id=wallet_id).first()
    assert wallet.balance == 0.00

def test_withdraw_wallet_wallet_not_found(client, auth_headers):
    """Return 409 when the wallet doesn't exist"""
    payload = {
        "currency": "MXN",
        "amount": 100.0
    }
    response = client.post(
        "/wallets/999/withdraw", 
        json=payload,
        headers=auth_headers
    )
    assert response.status_code == 409
    response_data = json.loads(response.data)
    assert "Wallet not found" in response_data["error"]

def test_withdraw_wallet_invalid_json(client, auth_headers, app):
    """Return 422 when JSON body fails validation"""
    # Missing required field 'amount'
    payload = {
        "currency": "USD"
    }
    wallet_id = app.test_wallet_ids['diana']
    response = client.post(f"/wallets/{wallet_id}/withdraw", json=payload, headers=auth_headers)
    
    assert response.status_code == 422
    response_data = json.loads(response.data)
    assert "errors" in response_data
    assert "amount" in response_data["errors"]

def test_withdraw_wallet_missing_currency(client, auth_headers, app):
    """Return 422 when currency is missing"""
    payload = {
        "amount": 100.0
        # Missing currency
    }
    wallet_id = app.test_wallet_ids['diana']
    response = client.post(f"/wallets/{wallet_id}/withdraw", json=payload, headers=auth_headers)
    
    assert response.status_code == 422
    response_data = json.loads(response.data)
    assert "errors" in response_data
    assert "currency" in response_data["errors"]

def test_withdraw_wallet_malformed_json(client, auth_headers, app):
    """Return 400 when JSON data is malformed"""
    wallet_id = app.test_wallet_ids['diana']
    response = client.post(
        f"/wallets/{wallet_id}/withdraw",
        data='{invalid json}',
        content_type="application/json",
        headers=auth_headers
    )
    assert response.status_code == 400
    # The endpoint uses abort() which returns HTML, not JSON
    assert "400 Bad Request" in response.data.decode('utf-8')

def test_withdraw_wallet_unauthorized(client, app):
    """Test that endpoint requires authentication"""
    payload = {
        "currency": "MXN",
        "amount": 100.0
    }
    wallet_id = app.test_wallet_ids['diana']
    response = client.post(
        f'/wallets/{wallet_id}/withdraw',
        json=payload
    )
    assert response.status_code == 401
    response_data = json.loads(response.data)
    assert "error" in response_data

def test_withdraw_wallet_zero_amount(client, auth_headers, app):
    """Test withdraw service with zero amount"""
    payload = {
        "currency": "MXN",
        "amount": 0.0
    }
    wallet_id = app.test_wallet_ids['diana']
    response = client.post(f'/wallets/{wallet_id}/withdraw', json=payload, headers=auth_headers)
    
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert response_data["message"] == "amount successfully subtracted"
    
    # Check that balance wasn't changed: 4500.50 - 0.0 = 4500.50
    wallet = WalletsModel.query.filter_by(id=wallet_id).first()
    assert wallet.balance == 4500.50

def test_withdraw_wallet_negative_amount(client, auth_headers, app):
    """Test withdraw service with negative amount"""
    payload = {
        "currency": "MXN",
        "amount": -100.0  # Negative amount
    }
    wallet_id = app.test_wallet_ids['diana']
    response = client.post(f'/wallets/{wallet_id}/withdraw', json=payload, headers=auth_headers)
    
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert response_data["message"] == "amount successfully subtracted"
    
    # Check that balance was increased: 4500.50 - (-100.0) = 4600.50
    wallet = WalletsModel.query.filter_by(id=wallet_id).first()
    assert wallet.balance == 4600.50

def test_withdraw_wallet_exact_balance(client, auth_headers, app):
    """Test withdraw service with exact balance amount"""
    payload = {
        "currency": "MXN",
        "amount": 4500.50  # Exact balance
    }
    wallet_id = app.test_wallet_ids['diana']
    response = client.post(f'/wallets/{wallet_id}/withdraw', json=payload, headers=auth_headers)
    
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert response_data["message"] == "amount successfully subtracted"
    
    # Check that balance is now zero: 4500.50 - 4500.50 = 0.0
    wallet = WalletsModel.query.filter_by(id=wallet_id).first()
    assert wallet.balance == 0.0