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
    """ Test fund service to response 200 """
    payload = {
        "currency": "USD",
        "amount": 1000
    }
    user_id = "f9e8d7c6-b5a4-43f2-1e0d-9c8b7a6f5e4d"
    response = client.post(
        f'/wallets/{user_id}/fund', 
        json=payload
    )
    assert response.status_code == 200
    assert json.loads(response.data)["message"] == "Amount added successfully"
    assert wallets_data[user_id]['balance'] == 19200 # 500 + (1000 * 18.7)

def test_fund_wallet_user_not_found(client):
    """ Return 404 when the wallet doesn't exists """
    response = client.post(
        "/wallets/nonexistent-user-id/fund", 
        json={"amount": 100, "currency": "MXN"}
    )
    assert response.status_code == 404
    assert "404 Not Found" in response.data.decode('utf-8')

def test_fund_wallet_invalid_json(client):
    """ Return 422 when JSON body fails validation """

    user_id = "f9e8d7c6-b5a4-43f2-1e0d-9c8b7a6f5e4d"
    response = client.post(
        f"/wallets/{user_id}/fund", 
        json={"currency": "USD"}
    )
    assert response.status_code == 422
    response_data = json.loads(response.data)
    assert "errors" in response_data

def test_fund_wallet_no_json_data(client):
    """ Return 400 when JSON data is malformed """
    user_id = "f9e8d7c6-b5a4-43f2-1e0d-9c8b7a6f5e4d"
    response = client.post(
        f"/wallets/{user_id}/fund",
        data='{invalid json}',
        content_type="application/json"
    )
    assert response.status_code == 400
    assert "400 Bad Request" in response.data.decode('utf-8')

def test_fund_wallet_empty_json_data(client):
    """ Return 400 when sending empty string as JSON """
    user_id = "f9e8d7c6-b5a4-43f2-1e0d-9c8b7a6f5e4d"
    response = client.post(
        f"/wallets/{user_id}/fund",
        data='',
        content_type="application/json"
    )
    assert response.status_code == 400
