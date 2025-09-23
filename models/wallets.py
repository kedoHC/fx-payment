from db import db

class WalletsModel(db.Model):  
    __tablename__ = "wallets"

    id = db.Column(db.String(36), primary_key=True)
    balance = db.Column(db.Float, nullable=False, default=0.0)  
    currency = db.Column(db.String(3), nullable=False, default="MXN")  
    recent_transactions = db.Column(db.Integer, nullable=False, default=0)  
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), unique=True, nullable=False)  
    user = db.relationship("UsersModel", back_populates="wallet")