from db import db


class WalletsModel(db.model):
  __tablename__ = "wallets"


  id = db.Columns(db.Integer, primary_key=True)
  balance = db.Columns(db.Float(precision= 2), unique=False, nullable=False)
  currency = db.Columns(db.String(3), unique=False, nullable=False)
  recent_transactions = db.Columns(db.Integer, unique=False, nullable=False)
  user_id = db.Columns(db.Integer, db.ForeingKey('users.id'), unique=False, nullable=False)
  user = db.relationship("UsersModel", back_populates="wallets")