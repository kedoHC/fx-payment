import pytest
import os
import sys
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from store.wallets import wallets_data

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture(autouse=True)
def setup_wallet_data():
    # Reset wallets data to known state before each test
    wallets_data.clear()
    wallets_data.update({
        # User "Diana" UUID with sufficient balance
        "f9e8d7c6-b5a4-43f2-1e0d-9c8b7a6f5e4d": {
            "balance": 4500.50,
            "currency": "MXN",
            "recent_transactions": 35
        },
        # User "Charlie" UUID with zero balance
        "a4b5c6d7-e8f9-40a1-8b2c-3d4e5f6a7b8c": {
            "balance": 0.00,
            "currency": "MXN",
            "recent_transactions": 0
        }
    })
    yield


def test_withdraw_wallet_success(client):
    """ Test withdraw service returns 200 with successful withdrawal """
    payload = {
        "currency": "MXN",
        "amount": 100.0
    }
    # Use Diana's wallet with sufficient balance (4500.50 MXN)
    user_id = "f9e8d7c6-b5a4-43f2-1e0d-9c8b7a6f5e4d"
    response = client.post(f'/wallets/{user_id}/withdraw', json=payload)
    
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert response_data["message"] == "amount successfully subtracted"
    # Check that balance was actually reduced: 4500.50 - 100.0 = 4400.50
    assert wallets_data[user_id]['balance'] == 4400.50


def test_withdraw_wallet_insufficient_balance(client):
    """ Return 404 when user has insufficient balance """
    payload = {
        "currency": "MXN",
        "amount": 1000.0  # More than Charlie's balance of 0.00
    }
    user_id = "a4b5c6d7-e8f9-40a1-8b2c-3d4e5f6a7b8c"
    response = client.post(f"/wallets/{user_id}/withdraw", json=payload)
    
    assert response.status_code == 404
    assert "404 Not Found" in response.data.decode('utf-8')
    # Check that balance wasn't changed
    assert wallets_data[user_id]['balance'] == 0.00


def test_withdraw_wallet_invalid_json(client):
    """ Return 422 when JSON body fails validation """
    # Missing required field 'amount'
    payload = {
        "currency": "USD"
    }
    user_id = "f9e8d7c6-b5a4-43f2-1e0d-9c8b7a6f5e4d"
    response = client.post(f"/wallets/{user_id}/withdraw", json=payload)
    
    assert response.status_code == 422
    response_data = json.loads(response.data)
    assert "errors" in response_data


def test_withdraw_wallet_malformed_json(client):
    """ Return 400 when JSON data is malformed """
    user_id = "f9e8d7c6-b5a4-43f2-1e0d-9c8b7a6f5e4d"
    response = client.post(
        f"/wallets/{user_id}/withdraw",
        data='{invalid json}',
        content_type="application/json"
    )
    assert response.status_code == 400
    assert "400 Bad Request" in response.data.decode('utf-8')
