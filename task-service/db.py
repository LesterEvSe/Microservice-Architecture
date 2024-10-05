import sqlite3
import json
import jwt
import datetime

SECRET_KEY = "OK_6SOME_SE5CRET"

class TaskService:
    def __init__(self, db_path='tasks.db'):
        # Create new DB, if doesn't exist
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.db_path = db_path

        # task_data. Must be initialize first
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_data (
                task TEXT NOT NULL CHECK (LENGTH(task) >= 1 AND LENGTH(task) <= 100),
                deadline DATETIME NOT NULL,
                description TEXT,
                todo_task BOOLEAN NOT NULL,
                PRIMARY KEY (task)
            )
        ''')

        # roles
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS roles (
                task TEXT NOT NULL CHECK (LENGTH(task) >= 1 AND LENGTH(task) <= 100),
                member TEXT NOT NULL CHECK (LENGTH(member) >= 4 AND LENGTH(member) <= 50),
                admin BOOLEAN NOT NULL,
                FOREIGN KEY (task) REFERENCES task_data(task)
            )
        ''')

        self.conn.commit()
        print(f"{self.db_path} created or verified successfully!")

    def __del__(self):
        self.cursor.close()
        self.conn.close()
        print(f"Connection to DB {self.db_path} closed.")


    def add_task(self, task, member, deadline, description=""):
        self.cursor.execute('''
            INSERT INTO task_data (task, member, deadline, todo_task, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (task, member, deadline, True, description))
        self.conn.commit()


    def delete_task(self, task, member):
        self.cursor.execute('DELETE FROM task_data WHERE task = ? AND member = ?', (task, member))
        self.conn.commit()


# Example of use
task_service = TaskService()

task_service.add_task('Development', 'Create API', 'user123', '2024-12-31 23:59:59', 'Development API')
task_service.delete_task('Development', 'Create API', 'user123')
