from db import db

class UsersModel(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(80), nullable=False)  
    email = db.Column(db.String(120), unique=True, nullable=False) 
    age = db.Column(db.Integer, nullable=False) 
    is_active = db.Column(db.Boolean, nullable=False, default=True) 
    wallet = db.relationship("WalletsModel", back_populates="user", uselist=False, cascade="all, delete-orphan")