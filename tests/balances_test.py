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
        # User "Diana" UUID with high balance
        "f9e8d7c6-b5a4-43f2-1e0d-9c8b7a6f5e4d": {
            "balance": 1870.0,  # Exactly 100 USD when converted
            "currency": "MXN",
            "recent_transactions": 35
        },
        # User "Bob" UUID with moderate balance
        "6d1f3e2a-0b9c-4d5e-8f7a-2b3c4d5e6f7a": {
            "balance": 935.0,  # Exactly 50 USD when converted
            "currency": "MXN",
            "recent_transactions": 12
        },
        # User "Charlie" UUID with zero balance
        "a4b5c6d7-e8f9-40a1-8b2c-3d4e5f6a7b8c": {
            "balance": 0.0,
            "currency": "MXN",
            "recent_transactions": 0
        }
    })
    yield


def test_get_balances_success(client):
    """ Test get balances service returns 200 with correct balances """
    # Use Diana's wallet with 1870 MXN (100 USD)
    user_id = "f9e8d7c6-b5a4-43f2-1e0d-9c8b7a6f5e4d"
    response = client.get(f'/wallets/{user_id}/balances')
    
    assert response.status_code == 200
    response_data = json.loads(response.data)
    
    # Check that both currencies are returned
    assert "mxn" in response_data
    assert "usd" in response_data
    
    # Check correct values: 1870 MXN = 100 USD (1870 / 18.70)
    assert response_data["mxn"] == 1870.0
    assert response_data["usd"] == 100.0


def test_get_balances_user_not_found(client):
    """ Return 404 when the user doesn't exist """
    response = client.get("/wallets/nonexistent-user-id/balances")
    assert response.status_code == 404
    assert "404 Not Found" in response.data.decode('utf-8')


def test_get_balances_zero_balance(client):
    """ Test get balances with zero balance """
    # Use Charlie's wallet with 0 MXN
    user_id = "a4b5c6d7-e8f9-40a1-8b2c-3d4e5f6a7b8c"
    response = client.get(f'/wallets/{user_id}/balances')
    
    assert response.status_code == 200
    response_data = json.loads(response.data)
    
    # Check that both currencies show zero
    assert response_data["mxn"] == 0.0
    assert response_data["usd"] == 0.0
