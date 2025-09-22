import os
from flask import Flask, request, jsonify
from utils.converter import converter
from utils.validate_user import validate_user
from utils.validate_balance import validate_balance
from store.wallets import wallets_data
from flask_smorest import abort
from schemas import FundSchema, ConvertSchema, WithdrawSchema, CreateUserSchema, CreateWalletSchema
from marshmallow import ValidationError
from db import db
from store.users import users_data
import uuid
# import models

def create_app(db_url=None):

  app = Flask(__name__)

  app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv('DATABASE_URL', "sqlite:///data.db")
  app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False

  db.init_app(app)

  URL_BASE = "/wallets"

  fund_schema = FundSchema()
  convert_schema = ConvertSchema()
  withdraw_schema = WithdrawSchema()
  create_user_schema = CreateUserSchema()
  create_wallet_schema = CreateWalletSchema()

  @app.get("/")
  def greet():
    """ Say hello to Monato Team!"""
    return {"message": "Hello Monato!"}

  @app.post("/users")
  def create_user():
    """ Create a new user """
    request_data = request.get_json(force=True)

    if not request_data:
      abort(400, description="Invalid JSON input.")

    try:
      validated_data = create_user_schema.load(request_data)
    except ValidationError as err:
      return jsonify({"errors": err.messages}), 422

    # Check if user with same email already exists
    for user in users_data:
      if user["email"] == validated_data["email"]:
        return jsonify({"error": "User with this email already exists"}), 409

    # Generate UUID for new user
    user_id = str(uuid.uuid4())
    new_user = {
      "id": user_id,
      "name": validated_data["name"],
      "email": validated_data["email"],
      "age": validated_data["age"],
      "is_active": validated_data.get("is_active", True)
    }
    
    users_data.append(new_user)
    return jsonify({"message": "User created successfully", "user_id": user_id}), 201

  @app.post("/wallets")
  def create_wallet():
    """ Create a new wallet for a user """
    request_data = request.get_json(force=True)

    if not request_data:
      abort(400, description="Invalid JSON input.")

    try:
      validated_data = create_wallet_schema.load(request_data)
    except ValidationError as err:
      return jsonify({"errors": err.messages}), 422

    user_id = validated_data["user_id"]
    
    # Check if user exists
    user_exists = any(user["id"] == user_id for user in users_data)
    if not user_exists:
      return jsonify({"error": "User not found"}), 404

    # Check if wallet already exists for this user
    if user_id in wallets_data:
      return jsonify({"error": "Wallet already exists for this user"}), 409

    # Convert initial balance to MXN if needed
    initial_balance = validated_data.get("initial_balance", 0.0)
    currency = validated_data.get("currency", "MXN")
    
    if currency == "USD":
      initial_balance = converter(initial_balance, "USD")
    
    wallets_data[user_id] = {
      "balance": initial_balance,
      "currency": "MXN",  # Always store in MXN
      "recent_transactions": 0
    }
    
    return jsonify({"message": "Wallet created successfully", "user_id": user_id}), 201

  @app.post(URL_BASE + "/<user_id>/fund")
  def fund_wallet(user_id):
    """ fun wallet by user id"""
    request_data = request.get_json(force=True)

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
    request_data = request.get_json(force=True)

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

    request_data = request.get_json(force=True)
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

  return app


app = create_app()
