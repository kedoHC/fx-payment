import pytest
import os
import sys
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from store.users import users_data

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_convert_currency_success(client):
    """ Test convert service returns 200 with correct conversion """
    payload = {
        "from_currency": "USD",
        "to_currency": "MXN",
        "amount": 100.0
    }
    user_id = "f9e8d7c6-b5a4-43f2-1e0d-9c8b7a6f5e4d"
    response = client.post(f'/wallets/{user_id}/convert', json=payload)
    
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert "amount" in response_data
    # 100 USD * 18.70 = 1870 MXN
    assert response_data["amount"] == 1870.0


def test_convert_currency_user_not_found(client):
    """ Return 404 when the user doesn't exist """
    payload = {
        "from_currency": "MXN",
        "to_currency": "USD", 
        "amount": 1870.0
    }
    response = client.post("/wallets/nonexistent-user-id/convert", json=payload)
    assert response.status_code == 404
    assert "404 Not Found" in response.data.decode('utf-8')


def test_convert_currency_invalid_json(client):
    """ Return 422 when JSON body fails validation """
    # Missing required field 'amount'
    payload = {
        "from_currency": "USD",
        "to_currency": "MXN"
    }
    user_id = "f9e8d7c6-b5a4-43f2-1e0d-9c8b7a6f5e4d"
    response = client.post(f"/wallets/{user_id}/convert", json=payload)
    
    assert response.status_code == 422
    response_data = json.loads(response.data)
    assert "errors" in response_data


def test_convert_currency_malformed_json(client):
    """ Return 400 when JSON data is malformed """
    user_id = "f9e8d7c6-b5a4-43f2-1e0d-9c8b7a6f5e4d"
    response = client.post(
        f"/wallets/{user_id}/convert",
        data='{invalid json}',
        content_type="application/json"
    )
    assert response.status_code == 400
    assert "400 Bad Request" in response.data.decode('utf-8')
