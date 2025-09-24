from db import db

class UsersModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    
    name = db.Column(db.String(80), nullable=True)  
    age = db.Column(db.Integer, nullable=True) 
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    country = db.Column(db.String(80), nullable=True)  
    wallet = db.relationship("WalletsModel", back_populates="user", uselist=False, cascade="all, delete-orphan")