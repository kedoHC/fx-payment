import os
from flask import Flask, request, jsonify
from sqlalchemy.sql.functions import user
from utils.converter import converter
from utils.validate_user import validate_user
from utils.validate_balance import validate_balance
from flask_smorest import abort
from schemas import FundSchema, ConvertSchema, WithdrawSchema, CreateUserSchema, CreateWalletSchema, UserListSchema, UserSchema, WalletSchema, WalletListSchema
from marshmallow import ValidationError
from db import db
import uuid
from models import UsersModel, WalletsModel

def create_app(db_url=None):

  app = Flask(__name__)

  app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv('DATABASE_URL', "sqlite:///data.db")
  app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False

  db.init_app(app)

  with app.app_context():
    db.create_all()

  URL_BASE = "/wallets"

  fund_schema = FundSchema()
  convert_schema = ConvertSchema()
  withdraw_schema = WithdrawSchema()
  create_user_schema = CreateUserSchema()
  create_wallet_schema = CreateWalletSchema()
  user_list_schema = UserListSchema(many=True)
  wallet_list_schema = WalletListSchema(many=True)
  user_schema = UserSchema()
  wallet_schema = WalletSchema()

  @app.get("/")
  def greet():
    """ Say hello to Monato Team!"""
    return {"message": "Hello Monato!"}

  # ==========================================================
  # ==========================================================
  # POST => CREATE USER
  # ==========================================================
  # ==========================================================

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

    # Check if user with same email already exists (DATABASE VERSION)
    existing_user = UsersModel.query.filter_by(email=validated_data["email"]).first()
    if existing_user:
      return jsonify({"error": "User with this email already exists"}), 409

    # Generate UUID for new user
    user_id = str(uuid.uuid4())
    
    # Create new user in database
    new_user = UsersModel(
      id=user_id,
      name=validated_data["name"],
      email=validated_data["email"],
      age=validated_data["age"],
      is_active=validated_data.get("is_active", True)
    )
    
    try:
      db.session.add(new_user)
      db.session.commit()
      return jsonify({"message": "User created successfully", "user_id": user_id}), 201
    except Exception as e:
      db.session.rollback()
      return jsonify({"error": "Failed to create user"}), 500

  # ==========================================================
  # ==========================================================
  # GET => GET ALL USERS
  # ==========================================================
  # ==========================================================

  @app.get("/users")
  def get_all_users():
    """ Get all users from the database """
    try:
      # Query all users from the database
      users = UsersModel.query.all()
      # Prepare user data with wallet information
      users_data = []
      for user in users:
        user_data = {
          "id": user.id,
          "name": user.name,
          "email": user.email,
          "age": user.age,
          "is_active": user.is_active,
          "wallet_id": user.wallet.id
        }
        users_data.append(user_data)
      
      # Serialize the data using the schema
      result = user_list_schema.dump(users_data)
      return jsonify({"users": result, "total": len(result)}), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to retrieve users"}), 500

  # ==========================================================
  # ==========================================================
  # GET => GET USER BY ID
  # ==========================================================
  # ==========================================================

  @app.get("/users/<user_id>")
  def get_user_by_id(user_id):
    """ Get a specific user by ID with wallet information """
    try:
      # Query user by ID from the database
      user = UsersModel.query.get(user_id)
      
      if not user:
        return jsonify({"error": "User not found"}), 404
      
      # Serialize the user data with wallet info using the schema
      result = user_schema.dump(user)
      return jsonify(result), 200
        
    except Exception as e:
      return jsonify({"error": "Failed to retrieve user"}), 500

  # ==========================================================
  # ==========================================================
  # POST => CREATE WALLET
  # ==========================================================
  # ==========================================================

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
    
    # Validate that the user exists
    existing_user = UsersModel.query.filter_by(id=user_id).first() 
    if not existing_user:
        return jsonify({"error": "The provided user is not registered"}), 404

        
    # Validate that the user already has a wallet
    existing_wallet = WalletsModel.query.filter_by(user_id=user_id).first()
    if existing_wallet:
        return jsonify({"error": "Wallet already exists for this user"}), 409

    # Convert initial balance to MXN if needed
    initial_balance = validated_data.get("initial_balance", 0.0)
    currency = validated_data.get("currency", "MXN")
    
    if currency == "USD":
      initial_balance = converter(initial_balance, "USD")
    
    # Create new wallet in database
    wallet_id = str(uuid.uuid4())

    new_wallet = WalletsModel(
      id=wallet_id,
      user_id=user_id,
      balance=initial_balance,
      currency="MXN",
      recent_transactions=0
    )
    # Store new wallet in the database
    try:
      db.session.add(new_wallet)
      db.session.commit()
      return jsonify({"message": "Wallet created successfully", "user_id": user_id, "wallet_id": wallet_id}), 201
    except Exception as e:
      db.session.rollback()
      return jsonify({"error": "Failed to create wallet"}), 500
  
  # ==========================================================
  # ==========================================================
  # GET => GET ALL WALLETS
  # ==========================================================
  # ==========================================================

  @app.get("/wallets")
  def get_all_wallets():
    """ Get all wallets from the database """
    try:
      # Query all wallets from the database
      wallets = WalletsModel.query.all()

      wallets_data = []
      for wallet in wallets:
        wallet_data = {
          "id": wallet.id,
          "balance": wallet.balance,
          "currency": wallet.currency,
          "recent_transactions": wallet.recent_transactions,
          "user": wallet.user,
        }
        wallets_data.append(wallet_data)
      
      # Serialize the data using the schema
      result = wallet_list_schema.dump(wallets)
      return jsonify({"wallets": result, "total": len(result)}), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to retrieve wallets"}), 500

  # ==========================================================
  # ==========================================================
  # GET => GET WALLET BY ID
  # ==========================================================
  # ==========================================================

  @app.get("/wallets/<wallet_id>")
  def get_wallet_by_id(wallet_id):
    """ Get a specific wallet by ID with wallet information """

    try:
      # Query user by ID from the database
      wallet = WalletsModel.query.get(wallet_id)
      
      if not wallet:
        return jsonify({"error": "Wallet not found"}), 404
      
      # Serialize the wallet data with wallet info using the schema
      result = wallet_schema.dump(wallet)
      return jsonify(result), 200
    except Exception as e:
      return jsonify({"error": "Failed to retrieve wallet"}), 500
  
  
  # ==========================================================
  # ==========================================================
  # POST => FUND WALLET
  # ==========================================================
  # ==========================================================

  @app.post(URL_BASE + "/<user_id>/fund")
  def fund_wallet(user_id):
    """ fund wallet by user id"""
    request_data = request.get_json(force=True)

    if not request_data:
      abort(400, description="Invalid JSON input.")

    try: 
      validated_data = fund_schema.load(request_data)
    except ValidationError as err:
      return jsonify({"errors": err.messages}), 422

    try: 
      existing_wallet = WalletsModel.query.filter_by(id=user_id).first()

      if not existing_wallet:
        return jsonify({"error": "Wallet not found"}), 409

      # Convert to MXN 
      amount_to_mx = converter(validated_data['amount'], validated_data['currency'])

      existing_wallet.balance += amount_to_mx
      db.session.commit()

      return jsonify({
        "message": "Balance updated successfully",
        "new_balance": existing_wallet.balance
      }), 200

    except Exception as e:
      return jsonify({"error": "Failed to fund wallet"}), 500

  # ==========================================================
  # ==========================================================
  # POST => CONVERT CURRENCY
  # ==========================================================
  # ==========================================================

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

  # ==========================================================
  # ==========================================================
  # POST => WITHDRAW
  # ==========================================================
  # ==========================================================

  @app.post(URL_BASE + "/<wallet_id>/withdraw")
  def withdraw_wallet(wallet_id):
    """ withdraw wallet by user id"""

    request_data = request.get_json(force=True)
    if not request_data:
      abort(400, description="Invalid JSON input.")

    try: 
      validated_data = withdraw_schema.load(request_data)
    except ValidationError as err:
      return jsonify({"errors": err.messages}), 422

    try:
      existing_wallet = WalletsModel.query.filter_by(id=wallet_id).first()

      if not existing_wallet:
        return jsonify({"error": "Wallet not found"}), 409

      amount_to_mx = converter(validated_data['amount'], validated_data['currency'])
      user_id = existing_wallet.user.id

      if validate_user(user_id) and validate_balance(user_id, amount_to_mx):

        existing_wallet.balance -= amount_to_mx
        db.session.commit()

        return {"message": "amount successfully subtracted"}
      else:
        return {"message": "Operation not allowed"}

    except Exception as e:
      return jsonify({"error": "Failed to withdraw wallet"}), 500

  
  # ==========================================================
  # ==========================================================
  # GET => BALANCES
  # ==========================================================
  # ==========================================================

  @app.get(URL_BASE + "/<user_id>/balances")
  def get_balances(user_id):
    """ get balances MXN and USD"""
    try:
      user = UsersModel.query.get(user_id)

      if user:
        amount_mxn = user.wallet.balance
        amount_usd = converter(amount_mxn, "MXN", "USD")
        return {"usd": float(f"{amount_usd:.2f}"), "mxn": float(f"{amount_mxn:.2f}")}

      else:
        return jsonify({"error": "User not found"}), 404

    except Exception as e:
      return jsonify({"error": "Failed to get balances"}), 500

  return app

app = create_app()
