import psycopg2

class UserDB:
    def __init__(self, dbname, user, password, host, port):
        self.connection = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self):
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE
        );
        '''
        self.cursor.execute(create_table_query)
        self.connection.commit()

    def add_user(self, username, email):
        insert_query = '''
        INSERT INTO users (username, email) VALUES (%s, %s) RETURNING id;
        '''
        self.cursor.execute(insert_query, (username, email))
        user_id = self.cursor.fetchone()[0]
        self.connection.commit()
        return user_id

    def get_users(self):
        self.cursor.execute("SELECT * FROM users;")
        return self.cursor.fetchall()

    def close(self):
        self.cursor.close()
        self.connection.close()
