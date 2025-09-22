import pytest
import os
import sys
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from store.users import users_data
from store.wallets import wallets_data

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture(autouse=True)
def cleanup_data():
    # Save original data
    original_wallets = wallets_data.copy()
    original_users = users_data.copy()
    yield
    # Restore original data
    wallets_data.clear()
    wallets_data.update(original_wallets)
    users_data.clear()
    users_data.extend(original_users)


def test_create_wallet_success_default_balance(client):
    """ Test wallet creation service returns 201 with default balance """
    # First, create a user
    user_payload = {
        "name": "Test User",
        "email": "test@example.com",
        "age": 30
    }
    user_response = client.post('/users', json=user_payload)
    assert user_response.status_code == 201
    user_id = json.loads(user_response.data)["user_id"]
    
    # Now create wallet for this user
    wallet_payload = {
        "user_id": user_id
    }
    response = client.post('/wallets', json=wallet_payload)
    assert response.status_code == 201
    response_data = json.loads(response.data)
    assert response_data["message"] == "Wallet created successfully"
    assert response_data["user_id"] == user_id
    
    # Verify wallet was created in wallets_data
    assert user_id in wallets_data
    assert wallets_data[user_id]["balance"] == 0.0
    assert wallets_data[user_id]["currency"] == "MXN"
    assert wallets_data[user_id]["recent_transactions"] == 0


def test_create_wallet_with_mxn_initial_balance(client):
    """ Test wallet creation with MXN initial balance """
    # Create a user first
    user_payload = {
        "name": "Test User 2",
        "email": "test2@example.com", 
        "age": 25
    }
    user_response = client.post('/users', json=user_payload)
    user_id = json.loads(user_response.data)["user_id"]
    
    # Create wallet with MXN balance
    wallet_payload = {
        "user_id": user_id,
        "initial_balance": 1000.0,
        "currency": "MXN"
    }
    response = client.post('/wallets', json=wallet_payload)
    assert response.status_code == 201
    
    # Verify wallet has correct MXN balance
    assert user_id in wallets_data
    assert wallets_data[user_id]["balance"] == 1000.0
    assert wallets_data[user_id]["currency"] == "MXN"


def test_create_wallet_with_usd_initial_balance(client):
    """ Test wallet creation with USD initial balance (converted to MXN) """
    # Create a user first
    user_payload = {
        "name": "Test User 3", 
        "email": "test3@example.com",
        "age": 28
    }
    user_response = client.post('/users', json=user_payload)
    user_id = json.loads(user_response.data)["user_id"]
    
    # Create wallet with USD balance
    wallet_payload = {
        "user_id": user_id,
        "initial_balance": 100.0,
        "currency": "USD"
    }
    response = client.post('/wallets', json=wallet_payload)
    assert response.status_code == 201
    
    # Verify wallet has converted USD to MXN (100 USD * 18.7 = 1870 MXN)
    assert user_id in wallets_data
    assert wallets_data[user_id]["balance"] == 1870.0  # 100 * 18.7
    assert wallets_data[user_id]["currency"] == "MXN"


def test_create_wallet_user_not_found(client):
    """ Test wallet creation for non-existent user returns 404 """
    wallet_payload = {
        "user_id": "non-existent-user-id"
    }
    response = client.post('/wallets', json=wallet_payload)
    assert response.status_code == 404
    response_data = json.loads(response.data)
    assert "User not found" in response_data["error"]


def test_create_wallet_duplicate_wallet(client):
    """ Test creating duplicate wallet for user returns 409 """
    # Create a user first
    user_payload = {
        "name": "Test User 4",
        "email": "test4@example.com",
        "age": 35
    }
    user_response = client.post('/users', json=user_payload)
    user_id = json.loads(user_response.data)["user_id"]
    
    # Create first wallet
    wallet_payload = {
        "user_id": user_id
    }
    response1 = client.post('/wallets', json=wallet_payload)
    assert response1.status_code == 201
    
    # Try to create second wallet for same user
    response2 = client.post('/wallets', json=wallet_payload)
    assert response2.status_code == 409
    response_data = json.loads(response2.data)
    assert "Wallet already exists for this user" in response_data["error"]


def test_create_wallet_missing_user_id(client):
    """ Test wallet creation without user_id returns 422 """
    wallet_payload = {
        "initial_balance": 100.0
        # Missing user_id
    }
    response = client.post('/wallets', json=wallet_payload)
    assert response.status_code == 422
    response_data = json.loads(response.data)
    assert "errors" in response_data
    assert "user_id" in response_data["errors"]


def test_create_wallet_invalid_balance(client):
    """ Test wallet creation with negative balance returns 422 """
    # Create a user first
    user_payload = {
        "name": "Test User 5",
        "email": "test5@example.com",
        "age": 40
    }
    user_response = client.post('/users', json=user_payload)
    user_id = json.loads(user_response.data)["user_id"]
    
    wallet_payload = {
        "user_id": user_id,
        "initial_balance": -100.0  # Invalid negative balance
    }
    response = client.post('/wallets', json=wallet_payload)
    assert response.status_code == 422
    response_data = json.loads(response.data)
    assert "errors" in response_data
    assert "initial_balance" in response_data["errors"]


def test_create_wallet_no_json_data(client):
    """ Test wallet creation with no JSON data returns 400 """
    response = client.post('/wallets', data='', content_type="application/json")
    assert response.status_code == 400
    assert "400 Bad Request" in response.data.decode('utf-8')


def test_create_wallet_malformed_json(client):
    """ Test wallet creation with malformed JSON returns 400 """
    response = client.post('/wallets', 
                          data='{invalid json}',
                          content_type="application/json")
    assert response.status_code == 400