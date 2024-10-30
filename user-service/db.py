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

    def get_jwt_for_username(self, username):
        self.cursor.execute('SELECT jwt FROM registration WHERE username = %s', (username,))
        return self.cursor.fetchone()
    
    def is_username_exist(self, username) -> bool:
        self.cursor.execute('SELECT * FROM registration WHERE username = %s', (username,))
        return self.cursor.fetchone()

    def is_user_email_exist(self, user_email) -> bool:
        self.cursor.execute('SELECT * FROM registration WHERE email = %s', (user_email,))
        return self.cursor.fetchone()
    
    def is_password_correct(self, user: User) -> bool:
        self.cursor.execute('SELECT password FROM registration WHERE username = %s', (user.username,))
        return self.cursor.fetchone()[0] == user.password

    def update_user_data_with_username(self, username, user: User):
        self.cursor.execute('''
            UPDATE registration 
            SET email = %s, username = %s, password = %s, jwt = %s 
            WHERE username = %s
        ''', (user.email, user.username, user.password, user.jwt_token, username))
        self.conn.commit()

    def register_user(self, user: User):
        self.cursor.execute('INSERT INTO registration (email, username, password, jwt) VALUES (%s, %s, %s, %s)',
                            (user.email, user.username, user.password, user.jwt_token))
        self.conn.commit()
