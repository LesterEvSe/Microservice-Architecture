import psycopg2

class TaskDB:
    def _create_tables(self):
        # task_data. Must be initialized before group_data table
        # task_id PRIMARY KEY not task, because the same task can exist in different groups
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_data (
                task_id SERIAL PRIMARY KEY,
                task_name VARCHAR(100) NOT NULL CHECK (LENGTH(task_name) >= 1 AND LENGTH(task_name) <= 100),
                description TEXT,
                deadline TIMESTAMPTZ NOT NULL,
                todo_task BOOLEAN NOT NULL
            )
        ''')

        # groups. Must be initialized before group_data table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS groups (
                group_id SERIAL PRIMARY KEY,
                group_name VARCHAR(100) NOT NULL CHECK (LENGTH(group_name) >= 1 AND LENGTH(group_name) <= 100),
                member VARCHAR(50) NOT NULL CHECK (LENGTH(member) >= 4 AND LENGTH(member) <= 50),
                admin BOOLEAN NOT NULL
            )
        ''')

        # group_data
        # ON DELETE CASCADE explanation below.
        # If we delete the parent table data, it will automatically delete data here as well
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS group_data (
                group_id INTEGER NOT NULL,
                task_id INTEGER NOT NULL,
                member VARCHAR(50) NOT NULL CHECK (LENGTH(member) >= 4 AND LENGTH(member) <= 50),
                
                FOREIGN KEY (group_id) REFERENCES groups(group_id) ON DELETE CASCADE,
                FOREIGN KEY (task_id) REFERENCES task_data(task_id) ON DELETE CASCADE,
                
                PRIMARY KEY (group_id, task_id, member)
            )
        ''')

    def __init__(self, dbname, user, password, host, port):
        # Create a new DB connection, if it doesn't exist
        self.conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        self.cursor = self.conn.cursor()

        self._create_tables()
        self.conn.commit()
        print(f"Database '{dbname}' created or verified successfully!")

    def __del__(self):
        self.cursor.close()
        self.conn.close()
        print(f"Connection to the task-service database closed.")

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
