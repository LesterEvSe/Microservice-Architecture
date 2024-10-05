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

        # task_data. Must be initialized first
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_data (
                task TEXT NOT NULL CHECK (LENGTH(task) >= 1 AND LENGTH(task) <= 100),
                deadline DATETIME NOT NULL,
                description TEXT,
                todo_task BOOLEAN NOT NULL,
                PRIMARY KEY (task)  -- Special for foreign key
            )
        ''')

        # groups. Must be initialized second
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS groups (
                "group" TEXT NOT NULL CHECK (LENGTH("group") >= 1 AND LENGTH("group") <= 100),
                admin TEXT NOT NULL CHECK (LENGTH(admin) >= 4 AND LENGTH(admin) <= 50),
                PRIMARY KEY ("group")
            )
        ''')

        # group_data
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS group_data (
                "group" TEXT NOT NULL CHECK (LENGTH("group") >= 1 AND LENGTH("group") <= 100),
                task TEXT NOT NULL CHECK (LENGTH(task) >= 1 AND LENGTH(task) <= 100),
                member TEXT NOT NULL CHECK (LENGTH(member) >= 4 AND LENGTH(member) <= 50),
                FOREIGN KEY (task) REFERENCES task_data(task),  -- Do not copy the data
                FOREIGN KEY ("group") REFERENCES groups("group")
            )
        ''')

        self.conn.commit()
        print(f"{self.db_path} created or verified successfully!")

    def __del__(self):
        self.cursor.close()
        self.conn.close()
        print(f"Connection to DB {self.db_path} closed.")


    # Expected this kind of structure
    '''
    data = [
        {
            "group": "group_name",
            "admin": "username",
            "tasks": [
                {
                    "task": "task_name",
                    "deadline": "time",
                    "description": "some_desc",
                    "todo_task": "true/false",
                    "members": ["first_user", "second_user"],
                },
                {
                    ...
                },
                ...
            ]"
        },
        {
            ...
        },
        ...
    ]
    '''

    # TODO Need to test
    def get_all_data_by_username(self, username):
        # SQL запит для отримання груп, завдань та деталей про них, де фігурує користувач
        self.cursor.execute('''
            SELECT g."group", g.admin, gd.task, td.deadline, td.description, td.todo_task
            FROM groups g
            JOIN group_data gd ON g."group" = gd."group"
            JOIN task_data td ON gd.task = td.task
            WHERE gd.member = ?
            GROUP BY g."group", g.admin, gd.task, td.deadline, td.description, td.todo_task
        ''', (username,))
        result = self.cursor.fetchall()

        # DS for store groups and tasks
        group_data = {}

        for row in result:
            group_name = row[0]
            group_admin = row[1]
            task_name = row[2]
            task_deadline = row[3]
            task_description = row[4]
            todo_task = row[5]

            # Get members for every task
            self.cursor.execute('''
                SELECT member
                FROM group_data
                WHERE task = ? AND "group" = ?
            ''', (task_name, group_name))
            members = [member[0] for member in self.cursor.fetchall()]

            # Create certain task
            task = {
                "task": task_name,
                "deadline": task_deadline,
                "description": task_description,
                "todo_task": todo_task,
                "members": members
            }

            # Create a group if it does not already exist
            if group_name not in group_data:
                group_data[group_name] = {
                    "group": group_name,
                    "admin": group_admin,
                    "tasks": []
                }
            group_data[group_name]["tasks"].append(task)
        return list(group_data.values())



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
