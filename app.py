from flask import Flask, request, jsonify
from utils.converter import converter
from utils.validate_user import validate_user
from utils.validate_balance import validate_balance
from store.wallets import wallets_data
from flask_smorest import abort

from schemas import FundSchema, ConvertSchema, WithdrawSchema
from marshmallow import ValidationError

app = Flask(__name__)
URL_BASE = "/wallets"

fund_schema = FundSchema()
convert_schema = ConvertSchema()
withdraw_schema = WithdrawSchema()

@app.get("/")
def greet():
  """ Say hello to Monato Team!"""
  return {"message": "Hello Monato!"}

@app.post(URL_BASE + "/<user_id>/fund")
def fund_wallet(user_id):
  """ fun wallet by user id"""
  request_data = request.get_json()

  if not request_data:
    abort(400, description="Invalid JSON input.")

  try: 
    validated_data = fund_schema.load(request_data)
  except ValidationError as err:
     return jsonify({"errors": err.messages}), 422

  if user_id in wallets_data:
    # Convert to MXN 
    amount_to_mx = converter(validated_data['amount'], validated_data['currency'])
    wallets_data[user_id]['balance'] += amount_to_mx
    return {"message": "Amount added successfully"}
  else:
    abort(404, message="Wallet not found")

@app.post(URL_BASE + "/<user_id>/convert")
def convert_currency(user_id):
  """ Convert currency """
  request_data = request.get_json()

  if not request_data:
    abort(400, description="Invalid JSON input.")

  try: 
    validated_data = convert_schema.load(request_data)
  except ValidationError as err:
     return jsonify({"errors": err.messages}), 422

  if validate_user(user_id):
    converted_amount = converter(**validated_data)
    return { "amount": converted_amount}
  else:
    abort(404, message="User not found")

@app.post(URL_BASE + "/<user_id>/withdraw")
def withdraw_wallet(user_id):
  """ withdraw wallet by user id"""

  request_data = request.get_json()
  if not request_data:
    abort(400, description="Invalid JSON input.")

  try: 
    validated_data = withdraw_schema.load(request_data)
  except ValidationError as err:
     return jsonify({"errors": err.messages}), 422

  amount_to_mx = converter(validated_data['amount'], validated_data['currency'])

  if validate_user(user_id) and validate_balance(user_id, amount_to_mx):
    wallets_data[user_id]['balance'] -= amount_to_mx
    return {"message": "amount successfully subtracted"}
  else:
    abort(404, message="Operation not allowed")

@app.get(URL_BASE + "/<user_id>/balances")
def get_balances(user_id):
  """ get balances MXN and USD"""

  if validate_user(user_id) and user_id in wallets_data:
    amount_mxn = wallets_data[user_id]['balance']
    amount_usd = converter(amount_mxn, "MXN", "USD")
    return {"usd": float(f"{amount_usd:.2f}"), "mxn": float(f"{amount_mxn:.2f}")}
  else:
    abort(404, message="Operation not allowed")
    

if __name__ == '__main__':
  app.run(debug=True, port=5001)