import jwt
import datetime

from db import UserDB
from Data.UserDTO import *
from Entity.User import *
from Mappings.mapper import *


SECRET_KEY = "OK_6SOME_SE5CRET"
DB = UserDB(dbname="users", user="user_admin", password="eighty9@doublet", host="user-db", port="5432")

# The data is hashed using an HS256 signature,
# so it cannot be tampered with (at least at the time of writing the program :D).
def _generate_jwt(username):
    expiration = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365 * 100)
    return jwt.encode({
        'username': username,
        'exp': expiration,
    }, SECRET_KEY, algorithm='HS256')

def _decode_jwt(jwt_token):
    try:
        token = jwt.decode(jwt_token, SECRET_KEY, algorithms=['HS256'])
        return (True, token['username'])
    except jwt.ExpiredSignatureError:
        return (False, "JWT token has expired")
    except jwt.InvalidTokenError:
        return (False, "Invalid JWT token")

def get_username_and_check_jwt(jwt_token):
    username = _decode_jwt(jwt_token)
    if not username[0]:
        return (False, {"error": username[1]})
    username = username[1]
    return DB.check_jwt(username, jwt_token)

def register_user(user_dto: UserDTO):
    user = dto_to_user_entity(user_dto)
    user.jwt_token = _generate_jwt(user.username)
    
    res = DB.register_user(user)
    if not res[0]:
        return res
    return (res[0], user.jwt_token)

def login_user(user_dto: UserDTO):
    user = dto_to_user_entity(user_dto)
    user.jwt_token = _generate_jwt(user.username)
    return DB.login_user(user)
