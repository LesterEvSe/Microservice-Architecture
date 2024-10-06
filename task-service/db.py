import sqlite3
import json

class TaskService:
    def _create_tables(self):
        # task_data. Must be initialized before group_data table
        # task_id PRIMARY KEY not task, because can the same task in the different groups
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_data (
                task_id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL CHECK (LENGTH(task) >= 1 AND LENGTH(task) <= 100),
                description TEXT,
                deadline DATETIME NOT NULL,
                todo_task BOOLEAN NOT NULL
            )
        ''')

        # groups. Must be initialized before group_data table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS groups (
                group_id INTEGER PRIMARY KEY AUTOINCREMENT,
                "group" TEXT NOT NULL CHECK (LENGTH("group") >= 1 AND LENGTH("group") <= 100),
                member TEXT NOT NULL CHECK (LENGTH(member) >= 4 AND LENGTH(member) <= 50),
                admin BOOLEAN NOT NULL
            )
        ''')

        # group_data
        # ON DELETE CASCADE explanation below.
        # If we delete the parent table data, it will be automatically deleted here as well
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS group_data (
                group_id TEXT NOT NULL CHECK (LENGTH("group") >= 1 AND LENGTH("group") <= 100),
                task_id INTEGER NOT NULL,
                member TEXT NOT NULL CHECK (LENGTH(member) >= 4 AND LENGTH(member) <= 50),
                
                FOREIGN KEY (group_id) REFERENCES groups(group_id) ON DELETE CASCADE,
                FOREIGN KEY (task_id) REFERENCES task_data(task_id) ON DELETE CASCADE,
                FOREIGN KEY (member) REFERENCES groups(member) ON DELETE CASCADE,
                
                PRIMARY KEY (group_id, task_id, member)
            )
        ''')

    def __init__(self, db_path='tasks.db'):
        # Create new DB, if doesn't exist
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()  # allow us to use DB operations
        self.db_path = db_path
        self.cursor.execute('PRAGMA foreign_keys = ON')

        self._create_tables()
        self.conn.commit()
        print(f"{self.db_path} created or verified successfully!")

    def __del__(self):
        self.cursor.close()
        self.conn.close()
        print(f"Connection to DB {self.db_path} closed.")

    def get_groups_for_user(self, username):
        try:
            self.cursor.execute('''
                SELECT DISTINCT g.group_id, g."group"
                FROM groups g
                WHERE g.member = ?
            ''', (username,))
            rows = self.cursor.fetchall()
        
            result = []
            for row in rows:
                result.append({
                    "group_id": row[0],
                    "group": row[1]
                })
            return json.dumps({"groups": result})

        except Exception as e:
            return json.dumps({"error": str(e)})

    # TODO think about where to add an error handler
    def add_group(self, group, member, admin: bool) -> bool:
        try:
            self.cursor.execute('''
                INSERT INTO groups ("group", member, admin) 
                VALUES (?, ?)
            ''', (group, member, admin))
            self.conn.commit()
            return True
        
        except sqlite3.IntegrityError:
            print(f"Error in add_group: {e}")
            self.conn.rollback()
            return False
        
        except Exception as e:
            print(f"Error in add_group: {e}")
            self.conn.rollback()  # Скасуємо зміни в разі будь-якої іншої помилки
            return False
    
    # Next 3 methods only for group admins
    def delete_group(self, group_id) -> str:
        pass

    def add_member_to_group(self, member, group_id) -> str:
        pass

    def delete_member_from_group(self, member, group_id) -> str:
        pass

    def is_user_admin_of_group(self, username, group) -> bool:
        pass

    def add_task(self, group, task, deadline, description, todo_task, member) -> bool:
        try:
            # 1. Add task to certain table
            self.cursor.execute('''
                INSERT INTO task_data (task, deadline, description, todo_task) 
                VALUES (?, ?, ?, ?)
            ''', (task, deadline, description, todo_task))
            task_id = self.cursor.lastrowid

            # 2. Connect task with group
            self.cursor.execute('''
                INSERT INTO group_data ("group", task_id, member) 
                VALUES (?, ?, ?)
            ''', (group, task_id, member))

            self.conn.commit()
            return True
        
        except Exception as e:
            print(f"Error in add_task: {e}")
            self.conn.rollback()
            return False

    # If the user is responsible for this task, or is an admin of group
    def delete_task(self, member, group_id, task_id):
        pass
        #self.cursor.execute('DELETE FROM task_data WHERE task = ?', (task,))
        #self.conn.commit()
    
    # Or maybe array of members ???
    def update_task(self, task_id, task, description, deadline, todo_task, member):
        pass

    def get_tasks_for_group(self, member, group_id):
        pass
    
    


# Example of use
# task_service = TaskService()

# task_service.add_task('Development', 'Create API', '2024-12-31 23:59:59', 'Development API', True, 'user123')
# task_service.delete_task('Development')
