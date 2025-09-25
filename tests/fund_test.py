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
        
        # Create test user and wallet
        test_user = UsersModel(
            email="fund@example.com",
            password=pbkdf2_sha256.hash("password123")
        )
        db.session.add(test_user)
        db.session.flush()
        
        # Create wallet with initial balance
        test_wallet = WalletsModel(
            user_id=test_user.id,
            balance=500.0,
            currency="MXN",
            recent_transactions=0
        )
        db.session.add(test_wallet)
        db.session.commit()
        
        # Store the user and wallet IDs for use in tests
        app.test_user_id = test_user.id
        app.test_wallet_id = test_wallet.id
        yield

def test_fund_wallet_success(client, auth_headers, app):
    """Test fund service returns 200"""
    payload = {
        "currency": "USD",
        "amount": 1000
    }
    wallet_id = app.test_wallet_id
    response = client.post(
        f'/wallets/{wallet_id}/fund', 
        json=payload,
        headers=auth_headers
    )
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert response_data["message"] == "Balance updated successfully"
    assert response_data["new_balance"] == 19200.0  # 500 + (1000 * 18.7)
    
    # Verify balance was updated in database
    wallet = WalletsModel.query.filter_by(id=wallet_id).first()
    assert wallet.balance == 19200.0

def test_fund_wallet_mxn_currency(client, auth_headers, app):
    """Test fund service with MXN currency"""
    payload = {
        "currency": "MXN",
        "amount": 1000
    }
    wallet_id = app.test_wallet_id
    response = client.post(
        f'/wallets/{wallet_id}/fund', 
        json=payload,
        headers=auth_headers
    )
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert response_data["message"] == "Balance updated successfully"
    assert response_data["new_balance"] == 1500.0  # 500 + 1000
    
    # Verify balance was updated in database
    wallet = WalletsModel.query.filter_by(id=wallet_id).first()
    assert wallet.balance == 1500.0

def test_fund_wallet_wallet_not_found(client, auth_headers):
    """Return 409 when the wallet doesn't exist"""
    response = client.post(
        "/wallets/999/fund", 
        json={"amount": 100, "currency": "MXN"},
        headers=auth_headers
    )
    assert response.status_code == 409
    response_data = json.loads(response.data)
    assert "Wallet not found" in response_data["error"]

def test_fund_wallet_invalid_json(client, auth_headers, app):
    """Return 422 when JSON body fails validation"""
    wallet_id = app.test_wallet_id
    response = client.post(
        f"/wallets/{wallet_id}/fund", 
        json={"currency": "USD"},  # Missing amount
        headers=auth_headers
    )
    assert response.status_code == 422
    response_data = json.loads(response.data)
    assert "errors" in response_data
    assert "amount" in response_data["errors"]

def test_fund_wallet_missing_currency(client, auth_headers, app):
    """Return 422 when currency is missing"""
    wallet_id = app.test_wallet_id
    response = client.post(
        f"/wallets/{wallet_id}/fund", 
        json={"amount": 100},  # Missing currency
        headers=auth_headers
    )
    assert response.status_code == 422
    response_data = json.loads(response.data)
    assert "errors" in response_data
    assert "currency" in response_data["errors"]

def test_fund_wallet_no_json_data(client, auth_headers, app):
    """Return 400 when JSON data is malformed"""
    wallet_id = app.test_wallet_id
    response = client.post(
        f"/wallets/{wallet_id}/fund",
        data='{invalid json}',
        content_type="application/json",
        headers=auth_headers
    )
    assert response.status_code == 400
    # The endpoint uses abort() which returns HTML, not JSON
    assert "400 Bad Request" in response.data.decode('utf-8')

def test_fund_wallet_empty_json_data(client, auth_headers, app):
    """Return 400 when sending empty string as JSON"""
    wallet_id = app.test_wallet_id
    response = client.post(
        f"/wallets/{wallet_id}/fund",
        data='',
        content_type="application/json",
        headers=auth_headers
    )
    assert response.status_code == 400
    # The endpoint uses abort() which returns HTML, not JSON
    assert "400 Bad Request" in response.data.decode('utf-8')

def test_fund_wallet_unauthorized(client, app):
    """Test that endpoint requires authentication"""
    payload = {
        "currency": "USD",
        "amount": 100
    }
    wallet_id = app.test_wallet_id
    response = client.post(
        f'/wallets/{wallet_id}/fund',
        json=payload
    )
    assert response.status_code == 401
    response_data = json.loads(response.data)
    assert "error" in response_data

def test_fund_wallet_negative_amount(client, auth_headers, app):
    """Test fund service with negative amount"""
    payload = {
        "currency": "USD",
        "amount": -100  # Negative amount
    }
    wallet_id = app.test_wallet_id
    response = client.post(
        f'/wallets/{wallet_id}/fund', 
        json=payload,
        headers=auth_headers
    )
    assert response.status_code == 200  # Negative amounts are allowed for funding
    response_data = json.loads(response.data)
    assert response_data["message"] == "Balance updated successfully"
    # 500 + (-100 * 18.7) = 500 - 1870 = -1370
    assert response_data["new_balance"] == -1370.0

def test_fund_wallet_zero_amount(client, auth_headers, app):
    """Test fund service with zero amount"""
    payload = {
        "currency": "USD",
        "amount": 0
    }
    wallet_id = app.test_wallet_id
    response = client.post(
        f'/wallets/{wallet_id}/fund', 
        json=payload,
        headers=auth_headers
    )
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert response_data["message"] == "Balance updated successfully"
    assert response_data["new_balance"] == 500.0  # 500 + 0