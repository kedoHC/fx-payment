from models import UsersModel

def validate_user(user_id):
    """ Validate user"""
    user = UsersModel.query.get(user_id)
    return user is not None and user.is_active