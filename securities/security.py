from werkzeug.security import safe_str_cmp
from models.user import UserModel

def login(username, password):
    user = UserModel.find_by_username(username)
    if user and user.password_is_valid(password):
        return user.generate_token(user.id)

def auth_by_token(token):
    return UserModel.decode_token(token)

def identity(payload):
    user_id = payload['identity']
    return UserModel.find_by_id(user_id)

