from db import TaskDB

DB = TaskDB(dbname="tasks", user="task_admin", password="A7noth56therUser", host="task-db", port="5432")

def get_groups_for_username(username):
    pass

def add_group(username, group: GroupDTO):
    pass

def delete_group(username, group: GroupDTO):
    pass

def add_member_to_group(member, group: GroupDTO):
    pass

def delete_member_from_group(member, group: GroupDTO):
    pass


def add_task(username, task: TaskDTO):
    pass

def delete_task_by_id(username, task: TaskDTO):
    pass

def update_task(username, task: TaskDTO):
    pass

def get_tasks_for_group(username, group: GroupDTO):
    pass