import sqlite3
import json
import jwt
import datetime

SECRET_KEY = "OK_6SOME_SE5CRET"

def generate_jwt(username):
    expiration = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365 * 100)
    return jwt.encode({
        'username': username,
        'exp': expiration
    }, SECRET_KEY, algorithm='HS256')

class UserService:
    def __init__(self, db_path='users.db'):
        # Create new DB, if doesn't exist
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.db_path = db_path
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS registration (
                email TEXT NOT NULL,
                username TEXT NOT NULL CHECK (LENGTH(username) >= 4 AND LENGTH(username) <= 50),
                password TEXT NOT NULL CHECK (LENGTH(password) >= 4 AND LENGTH(password) <= 50),
                jwt TEXT NOT NULL
            )
        ''')

        self.conn.commit()
        print(f"{self.db_path} created or verified successfully!")

    def __del__(self):
        self.cursor.close()
        self.conn.close()
        print(f"Connection to DB {self.db_path} closed.")

    # TODO maybe need to return JWT Key too
    def register_user(self, json_data):
        data = json.loads(json_data)
        email = data['email']
        username = data['username']
        password = data['password']
        
        # Check if user exist
        self.cursor.execute('SELECT * FROM registration WHERE email = ? OR username = ?', (email, username))
        if self.cursor.fetchone():
            return False
        
        jwt_token = generate_jwt(username)
        self.cursor.execute('INSERT INTO registration (email, username, password, jwt) VALUES (?, ?, ?, ?)',
                            (email, username, password, jwt_token))
        self.conn.commit()
        return True
    
    def login_user(self, json_data):
        data = json.loads(json_data)
        username = data['username']
        password = data['password']

        # Check if user exist
        self.cursor.execute('SELECT password FROM registration WHERE username = ?', (username,))
        user_record = self.cursor.fetchone()
        return user_record is not None and user_record[0] == password


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
