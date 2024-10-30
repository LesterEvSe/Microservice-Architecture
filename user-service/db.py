import psycopg2
from Entity.User import *

class UserDB:
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


    def register_user(self, user: User):
        self.cursor.execute('SELECT * FROM registration WHERE email = %s', (user.email,))
        if self.cursor.fetchone():
            return (False, "Email already exists.")

        self.cursor.execute('SELECT * FROM registration WHERE username = %s', (user.username,))
        if self.cursor.fetchone():
            return (False, "Username already exists.")
        
        self.cursor.execute('INSERT INTO registration (email, username, password, jwt) VALUES (%s, %s, %s, %s)',
                            (user.email, user.username, user.password, user.jwt_token))
        self.conn.commit()
        return (True,)
    
    def login_user(self, user: User):
        # Check if user exist
        self.cursor.execute('SELECT password FROM registration WHERE username = %s', (user.username,))
        user_record = self.cursor.fetchone()
        if user_record is None or user_record[0] != user.password:
            return False
        
        self.cursor.execute('UPDATE registration SET jwt = %s WHERE username = %s', (user.jwt_token, user.username))
        self.conn.commit()
        return True
    
    def check_jwt(self, username, jwt):
        self.cursor.execute('SELECT jwt FROM registration WHERE username = %s', (username,))
        user_record = self.cursor.fetchone()

        if user_record is None:
            return (False, {"error": "User does not exist"})
        if user_record[0] != jwt:
            return (False, {"error": "JWT key does not correct"})
        return (True, username)



#########
# TESTS #
#########
import os
#import json

def test_user_service():
    db_path = 'Test.db'
    user_service = UserDB(db_path)
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
