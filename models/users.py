from db import db


class UsersModel(db.model):
  __tablename__ = "users"


  id = db.Columns(db.Integer, primary_key=True)
  name = db.Columns(db.String(80), unique=True, nullable=False)
  email = db.Columns(db.String(80), unique=True, nullable=False)
  age = db.Columns(db.Integer, unique=False, nullable=False)
  is_active = db.Columns(db.Boolean, unique=False, nullable=False)
  wallet_id = db.Columns(db.Integer, unique=False, nullable=False)
  wallet = db.relationship("WalletsModel", back_populates="user", lazy="dynamic" )
