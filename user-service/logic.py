import jwt
import datetime

# for google oauth
import secrets
import base64
from google.oauth2 import id_token
from google.auth.transport import requests

from db import UserDB
from Data.UserDTO import *
from Data.GoogleDTO import *
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
        return (False, username[1])
    username = username[1]

    if not DB.is_username_exist(username):
        return (False, "User doesn't exist.")
    
    db_jwt_token = DB.get_jwt_for_username(username)
    if db_jwt_token != jwt_token:
        return (False, "JWT key doesn't correct.")
    return (True, username)

def is_user_exist(username):
    return DB.is_username_exist(username)

def register_user(user_dto: UserDTO):
    user = dto_to_user_entity(user_dto, _generate_jwt(user_dto.username))

    if DB.is_user_email_exist(user.email):
        return (False, "Email already exists.")
    if DB.is_username_exist(user.username):
        return (False, "Username already exists.")
    
    DB.register_user(user)
    return (True, user.jwt_token)

def login_user(user_dto: UserDTO):
    user = dto_to_user_entity(user_dto, _generate_jwt(user_dto.username))

    if not DB.is_username_exist(user.username):
        return (False, "User doesn't exist.")
    if not DB.is_password_correct(user):
        return (False, "Login or password doesn't correct.")
    
    DB.update_user_data_with_username(user.username, user)
    return (True, user.jwt_token)

# Official Doc https://developers.google.com/identity/gsi/web/guides/verify-google-id-token#python
def google_sign_up(google: GoogleDTO):
    try:
        # Specify the CLIENT_ID of the app that accesses the backend:
        idinfo = id_token.verify_oauth2_token(google.jwt, requests.Request(), "455836721320-ed0nlrlgjjp4m26dltrr7nqo3or5emn2.apps.googleusercontent.com")  # client id
        email = idinfo.get('email')
        if not email:
            raise ValueError("google token without 'email'")
        
    except ValueError as e:
        return (False, f"Invalid Google token: {e}")
    
    email_exist = DB.is_user_email_exist(email)
    if email_exist:
        username = DB.get_username_for_email(email)
        jwt_key = _generate_jwt(username)
        DB.update_jwt_with_email(jwt_key, email)
        return (True, jwt_key)
    
    elif not email_exist and google.username:
        raw_bytes = secrets.token_bytes(32)
        password = base64.b64encode(raw_bytes).decode('utf-8')
        user = dto_to_user_entity(UserDTO(google.username, email, password), _generate_jwt(google.username))
        DB.register_user(user)
        return (True, user.jwt_token)
    
    else:
        return (False, "user does not exist")
    