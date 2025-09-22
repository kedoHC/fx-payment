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
def cleanup_data():
    wallets_data.clear()
    wallets_data['f9e8d7c6-b5a4-43f2-1e0d-9c8b7a6f5e4d'] = {'balance': 500}
    yield


def test_fund_wallet_success(client):
    """ Test fund service to response 200"""
    payload = {
        "currency": "USD",
        "amount": 1000
    }
    response = client.post('/wallets/f9e8d7c6-b5a4-43f2-1e0d-9c8b7a6f5e4d/fund', json=payload)
    assert response.status_code == 200
    assert json.loads(response.data)["message"] == "Amount added successfully"
    assert wallets_data['f9e8d7c6-b5a4-43f2-1e0d-9c8b7a6f5e4d']['balance'] == 19200 # 500 + (1000 * 18.7)