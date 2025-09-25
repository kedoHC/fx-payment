from models import UsersModel
from db import db

def validate_user(user_id):
    """ Validate user"""
    user = db.session.get(UsersModel, user_id)
    return user is not None and user.is_active