import sqlite3  # TODO delete later
import psycopg2
import json
import jwt
import datetime

SECRET_KEY = "OK_6SOME_SE5CRET"

# The data is hashed using an HS256 signature,
# so it cannot be tampered with (at least at the time of writing the program :D).
def generate_jwt(username):
    expiration = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365 * 100)
    return jwt.encode({
        'username': username,
        'exp': expiration,
    }, SECRET_KEY, algorithm='HS256')

def decode_jwt(jwt_token):
    try:
        token = jwt.decode(jwt_token, SECRET_KEY, algorithms=['HS256'])
        return (True, token['username'])
    except jwt.ExpiredSignatureError:
        return (False, "JWT token has expired")
    except jwt.InvalidTokenError:
        return (False, "Invalid JWT token")


class UserService:
    def __init__(self, dbname, user, password, host, port):
        self.conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        self.cursor = self.conn.cursor()

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS registration (
                email VARCHAR(255) NOT NULL UNIQUE,
                username VARCHAR(50) NOT NULL CHECK (LENGTH(username) >= 4 AND LENGTH(username) <= 50) UNIQUE,
                password VARCHAR(50) NOT NULL CHECK (LENGTH(password) >= 4 AND LENGTH(password) <= 50),
                jwt TEXT NOT NULL,
    
                PRIMARY KEY (email, username)
            );
            ''')
        self.conn.commit()
        print(f"Database '{dbname}' created or verified successfully!")

    def __del__(self):
        self.cursor.close()
        self.conn.close()
        print("Connection to the user-service database closed.")


    def register_user(self, json_data):
        email = json_data['email']
        username = json_data['username']
        password = json_data['password']

        self.cursor.execute('SELECT * FROM registration WHERE email = ?', (email,))
        if self.cursor.fetchone():
            return (False, "Email already exists.")

        self.cursor.execute('SELECT * FROM registration WHERE username = ?', (username,))
        if self.cursor.fetchone():
            return (False, "Username already exists.")
        
        jwt_token = generate_jwt(username)
        self.cursor.execute('INSERT INTO registration (email, username, password, jwt) VALUES (?, ?, ?, ?)',
                            (email, username, password, jwt_token))
        self.conn.commit()
        return (True, jwt_token)
    
    def login_user(self, json_data):
        username = json_data['username']
        password = json_data['password']

        # Check if user exist
        self.cursor.execute('SELECT password FROM registration WHERE username = ?', (username,))
        user_record = self.cursor.fetchone()
        if user_record is None or user_record[0] != password:
            return False
        
        jwt_token = generate_jwt(username)
        self.cursor.execute('UPDATE registration SET jwt = ? WHERE username = ?', (jwt_token, username))
        self.conn.commit()
        return jwt_token
    
    # If None, then correct
    def check_jwt(self, jwt):
        username = decode_jwt(jwt)
        if not username[0]:
            return (False, json.dumps({"error": username[1]}))
        username = username[1]
        
        self.cursor.execute('SELECT jwt FROM registration WHERE username = ?', (username,))
        user_record = self.cursor.fetchone()

        if user_record is None:
            return (False, json.dumps({"error": "User does not exist"}))
        if user_record[0] != jwt:
            return (False, json.dumps({"error": "JWT key does not correct"}))
        return (True, username)



#########
# TESTS #
#########
import os

def test_user_service():
    db_path = 'Test.db'
    user_service = UserService(db_path)
    register_data = json.dumps({
        'email': 'test0@example.com',
        'username': 'Test0',
        'password': '1234at'
    })

    # Registration
    registration_result = user_service.register_user(register_data)
    assert(registration_result == True)

    reg_res2 = user_service.register_user(register_data)
    assert(reg_res2 == False)

    login_data_correct = json.dumps({
        'username': 'Test0',
        'password': '1234at'
    })
    login_result = user_service.login_user(login_data_correct)
    assert(login_result == True)


    login_data_wrong_username = json.dumps({
        'username': 'unknown_name',
        'password': '1234at'
    })
    login_result_username = user_service.login_user(login_data_wrong_username)
    assert(login_result_username == False)

    login_data_wrong_password = json.dumps({
        'username': 'Test0',
        'password': 'wrong_password'
    })
    login_result_password = user_service.login_user(login_data_wrong_password)
    assert(login_result_password == False)
    os.remove(db_path)

# test_user_service()
