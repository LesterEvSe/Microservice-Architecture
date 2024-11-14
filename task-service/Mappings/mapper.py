from datetime import datetime

from Data.GroupDTO import *
from Entity.Group import *

from Data.TaskDTO import *
from Entity.Task import *

from Data.GroupDataDTO import *
from Entity.GroupData import *


# Group
def json_to_group_dto(json_data):
    try:
        # if group else group_id. Priority important!
        group = json_data.get("group") if "group" in json_data else json_data.get("group_id")
        member = json_data.get("admin") if "admin" in json_data else json_data.get("member")

        if not group or not member:
            raise ValueError("incomplete group data")

        return (True, GroupDTO(group, member))
    except (TypeError, ValueError) as e:
        return (False, f"error when extracting data: {e}")

def group_dto_to_group_entity(group_dto: GroupDTO, admin: bool):
    return Group(group=group_dto.group, member=group_dto.member, admin=admin)

def group_entity_to_group_dto(group: Group):
    return GroupDTO(group=group.group, member=group.member)


# Task
def json_to_task_dto(json_data):
    try:
        # If task_name, else task_id. Priority important!
        task = json_data.get("task_name") if "task_name" in json_data else json_data.get("task_id")
        description = json_data.get("description"),
        deadline = datetime.fromisoformat(json_data.get("deadline")),
        todo_task = json_data.get("todo_task") == "True",
        members = json_data.get("members")

        if not task or not description or not deadline or not todo_task:
            raise ValueError("incomplete task data")

        return (True, TaskDTO(task, description, deadline, todo_task, members))
    except (TypeError, ValueError) as e:
        return (False, f"error when extracting data: {e}")

def task_dto_to_task_entity(task_dto: TaskDTO):
    return Task(task_dto.task, task_dto.description, task_dto.deadline, task_dto.todo_task, task_dto.members)

def task_entity_to_task_dto(task: Task):
    return TaskDTO(task.task, task.description, task.deadline, task.todo_task, task.members)


# GroupData
def json_to_group_data_dto(json_data):
    try:
        group_id = json_data.get("group_id")
        task_id = json_data.get("task_id")
        user = json_data.get("user")

        if not group_id or not task_id or not user:
            raise ValueError("incomplete group data")

        return (True, GroupDataDTO(group_id, task_id, user))
    except (TypeError, ValueError) as e:
        return (False, f"error when extracting data: {e}")

def group_data_dto_to_entity(group_data_dto: GroupDataDTO):
    return GroupData(group_data_dto.group_id, group_data_dto.task_id, group_data_dto.user)

def group_data_entity_to_dto(group_data: GroupData):
    pass