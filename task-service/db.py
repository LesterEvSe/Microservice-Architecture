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

        # task_data
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_data (
                "group" TEXT NOT NULL CHECK (LENGTH("group") >= 1 AND LENGTH("group") <= 100),
                task TEXT NOT NULL CHECK (LENGTH(task) >= 1 AND LENGTH(task) <= 100),
                member TEXT NOT NULL CHECK (LENGTH(member) >= 4 AND LENGTH(member) <= 50),
                deadline DATETIME NOT NULL,
                description TEXT, -- No size limit
                todo_task BOOLEAN NOT NULL,
                PRIMARY KEY ("group", task, member)
            )
        ''')
        self.conn.commit()
        print(f"{self.db_path} created or verified successfully!")

    def __del__(self):
        self.cursor.close()
        self.conn.close()
        print(f"Connection to DB {self.db_path} closed.")


    def add_task(self, group, task, member, deadline, description=""):
        self.cursor.execute('''
            INSERT INTO task_data ("group", task, member, deadline, todo_task, description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (group, task, member, deadline, True, description))
        self.conn.commit()


    def delete_task(self, group, task, member):
        self.cursor.execute('DELETE FROM task_data WHERE "group" = ? AND task = ? AND member = ?', (group, task, member))
        self.conn.commit()


# Example of use
task_service = TaskService()

task_service.add_task('Development', 'Create API', 'user123', '2024-12-31 23:59:59', 'Development API')
task_service.delete_task('Development', 'Create API', 'user123')
