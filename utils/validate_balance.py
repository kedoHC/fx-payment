from models import WalletsModel

def validate_balance(user_id, amount):
    """ Check if the user has sufficient balance in his account """
    wallet = WalletsModel.query.filter_by(user_id=user_id).first()
    if not wallet:
        return False
    return wallet.balance >= amount