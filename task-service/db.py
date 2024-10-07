import sqlite3

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
        # If we delete the parent table data, it will be automatically deleted data here as well
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
        
            result = {"group_id": [], "group": []}
            for row in rows:
                result["group_id"].append(row[0])
                result["group"].append(row[1])
            return result

        except Exception as e:
            print(f"Error in get_groups_for_user: {str(e)}")
            return False

    def add_group(self, group, member) -> bool:
        try:
            self.cursor.execute('''
                INSERT INTO groups ("group", member, admin) 
                VALUES (?, ?, ?)
            ''', (group, member, True))
            self.conn.commit()
            return True
        
        except (sqlite3.IntegrityError, Exception) as e:
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

    def is_user_admin_of_group(self, username, group_id) -> bool:
        pass

    def is_user_in_group(self, username, group_id) -> bool:
        pass

    # TODO need to recode
    def add_task(self, group_id, task, deadline, description, todo_task, member: list) -> bool:
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

    # If the user is responsible for this task, or is an admin of the group.
    # Perhaps this will be enough, the rest will be deleted thanks to FOREIGN KEY
    def delete_task(self, task_id) -> bool:
        pass
        #self.cursor.execute('DELETE FROM task_data WHERE task = ?', (task,))
        #self.conn.commit()
    
    def update_task(self, task_id, task, description, deadline, todo_task, member: list) -> bool:
        pass

    def get_tasks_for_group(self, group_id):
        pass
    
    


# Example of use
# task_service = TaskService()

# task_service.add_task('Development', 'Create API', '2024-12-31 23:59:59', 'Development API', True, 'user123')
# task_service.delete_task('Development')
