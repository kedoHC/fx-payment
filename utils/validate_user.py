
from store.users import users_data


def validate_user(id):
  """ Validate user"""
  valid_user = False

  for user in users_data:
    if user["id"] == id:
      valid_user = True
      
  return valid_user

      
    

