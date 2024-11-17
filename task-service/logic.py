from datetime import datetime
from db import TaskDB
from Mappings.mapper import *

from Data.GroupDTO import *
from Entity.Group import *

from Data.TaskDTO import *

from Data.GroupDataDTO import *
from Entity.GroupData import *


DB = TaskDB(dbname="tasks", user="task_admin", password="A7noth56therUser", host="task-db", port="5432")

def get_groups_for_username(username):
    return DB.get_groups_for_username(username)

def is_user_admin_of_group(group_dto: GroupDTO):
    return DB.is_user_admin_of_group(group_dto.member, group_dto.group)

def get_group_users(group_dto: GroupDTO):
    if not DB.is_user_in_group(group_dto.member, group_dto.group):
        return (False, "the user is not in this group")
    return (True, DB.get_group_users(group_dto.group))

def add_group(group_dto: GroupDTO):
    group = group_dto_to_group_entity(group_dto, admin=True)
    group_id = DB.add_group(group.group)

    group.group = group_id
    (res, error) = DB.add_member_to_group(group)
    if not res:
        return (res, error)
    return (True, group_id)

# Check if user is admin
def delete_group(group_dto: GroupDTO) -> tuple[bool, str]:
    if not is_user_admin_of_group(group_dto):
        return "user is not admin of the group."
    
    (res, err) = DB.transaction(DB.delete_group_by_id, group_dto.group)
    return None if res else err

def add_member_to_group(member, group_dto: GroupDTO):
    if not is_user_admin_of_group(group_dto):
        return "user is not admin of the group."
    
    group = group_dto_to_group_entity(GroupDTO(group_dto.group, member), admin=False)
    (res, err) = DB.transaction(DB.add_member_to_group, group)
    return None if res else err

def delete_member_from_group(member, group_dto: GroupDTO) -> str:
    if not is_user_admin_of_group(group_dto):
        return "user is not admin of the group."
    
    (res, err) = DB.transaction(DB.delete_member_from_group, member, group_dto.group)
    return None if res else err


def add_task(username, group_id, task_dto: TaskDTO):
    if not DB.is_user_in_group(username, group_id):
        return (False, "user is not in the group.")
    
    task = task_dto_to_task_entity(task_dto)
    task_id = DB.add_task(task)
    
    (res, err) = DB.transaction(DB.add_task_to_group, group_id, task_id)
    if not res:
        return (False, err)
    else:
        return (True, task_id)

def update_task(group_data_dto: GroupDataDTO, task_dto: TaskDTO):
    if not DB.is_user_in_group(group_data_dto.user, group_data_dto.group_id):
        return "user is not in the group"
    
    if not DB.is_task_exist(group_data_dto.task_id):
        return "task does not exist."
    
    group_data = group_data_dto_to_entity(group_data_dto)
    task = task_dto_to_task_entity(task_dto)

    (res, err) = DB.update_task(group_data.task_id, task)
    return None if res else err

def delete_task(group_data_dto: GroupDataDTO):
    if not DB.is_user_in_group(group_data_dto.user, group_data_dto.group_id):
        return "user is not in the group."
    
    if not DB.is_task_exist(group_data_dto.task_id):
        return "task does not exist."
    
    (res, err) = DB.transaction(DB.delete_task, group_data_dto.task_id)
    return None if res else err


def get_tasks_for_group(group: GroupDTO):
    if not DB.is_user_in_group(group.member, group.group):
        return (False, "user is not in the group.")
    
    tasks = DB.get_tasks_for_group(group.group)
    print(tasks)
    if 'deadline' in tasks:
        tasks['deadline'] = [dt.isoformat() if isinstance(dt, datetime) else dt for dt in tasks['deadline']]
    return (True, tasks)

def get_assigned_users_to_task(group_data: GroupDataDTO):
    if not DB.is_user_in_group(group_data.user, group_data.group_id):
        return (False, "user is not in the group.")
    return (True, DB.get_assigned_users_to_task(group_data.task_id))
