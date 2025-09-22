from flask import Flask, jsonify, request
from utils.converter import converter
from utils.validate_user import validate_user
from utils.validate_balance import validate_balance
from store.wallets import wallets_data
from flask_smorest import abort


app = Flask(__name__)
URL_BASE = "/wallets"

@app.get("/")
def greet():
  """ Say hello to Monato Team!"""
  return {"message": "Hello Monato!"}

@app.post(URL_BASE + "/<user_id>/fund")
def fund_wallet(user_id):
  """ fun wallet by user id"""

  request_data = request.get_json()
  if user_id in wallets_data:
    # Convert to MXN 
    amount_to_mx = converter(request_data['amount'], request_data['currency'])
    wallets_data[user_id]['balance'] += amount_to_mx
    return {"message": "Amount added successfully"}
  else:
    abort(404, message="Wallet not found")

@app.post(URL_BASE + "/<user_id>/convert")
def convert_currency(user_id):
  """ Convert currency """

  request_data = request.get_json()
  print(request_data)
  if validate_user(user_id):
    converted_amount = converter(**request_data)
    return { "amount": converted_amount}
  else:
    abort(404, message="User not found")

@app.post(URL_BASE + "/<user_id>/withdraw")
def withdraw_wallet(user_id):
  """ withdraw wallet by user id"""

  request_data = request.get_json()
  amount_to_mx = converter(**request_data)

  if validate_user(user_id) and validate_balance(user_id, amount_to_mx):
    wallets_data[user_id]['balance'] -= amount_to_mx
    return {"message": "amount successfully subtracted"}
  else:
    abort(404, message="Operation not allowed")

@app.get(URL_BASE + "/<user_id>/balances")
def get_balances(user_id):
  """ get balances MXN and USD"""

  amount_mxn = wallets_data[user_id]['balance']
  amount_usd = converter (wallets_data[user_id]['balance'], "MXN", "USD")

  if validate_user(user_id):
    return {"usd": float(f"{amount_usd:.2f}"), "mxn": float(f"{amount_mxn:.2f}")}
  else:
    abort(404, message="Operation not allowed")
    

if __name__ == '__main__':
  app.run(debug=True, port=5001)