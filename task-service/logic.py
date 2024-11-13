from db import TaskDB
from Mappings.mapper import *

from Data.GroupDTO import *
from Data.TaskDTO import *
from Entity.Group import *

DB = TaskDB(dbname="tasks", user="task_admin", password="A7noth56therUser", host="task-db", port="5432")


def get_groups_for_username(username):
    return DB.get_groups_for_username(username)

def is_user_admin_of_group(group_dto: GroupDTO):
    return DB.is_user_admin_of_group(group_dto.member, group_dto.group)

def get_group_users(group_dto: GroupDTO):
    admin = is_user_admin_of_group(group_dto)
    group = group_dto_to_group_entity(group_dto, admin)
    return DB.get_group_users(group)

def add_group(group_dto: GroupDTO):
    group = group_dto_to_group_entity(group_dto, admin=True)
    return DB.add_group(group)

# Check if user is admin
def delete_group(group_dto: GroupDTO) -> tuple[bool, str]:
    if not is_user_admin_of_group(group_dto):
        return (False, "user is not admin of the group.")
    
    (res, err) = DB.delete_group_by_id(group_dto.group)
    if not res:
        return (res, err)
    return (True, None)

def add_member_to_group(member, group_dto: GroupDTO):
    if not is_user_admin_of_group(group_dto):
        return (False, "user is not admin of the group.")
    
    (res, err) = DB.add_member_to_group(member, group_dto.group)
    if not res:
        return (res, err)
    return (True, None)

def delete_member_from_group(member, group_dto: GroupDTO):
    if not is_user_admin_of_group(group_dto):
        return (False, "user is not admin of the group.")
    
    (res, err) = DB.delete_member_from_group(member, group_dto.group)
    if not res:
        return (res, err)
    return (True, None)

def get_tasks_for_group(username, group: GroupDTO):
    pass


def add_task(username, task: TaskDTO):
    pass

def delete_task_by_id(username, task: TaskDTO):
    pass

def update_task(username, task: TaskDTO):
    pass