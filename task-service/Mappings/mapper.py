from Data.GroupDTO import *
from Entity.Group import *

def json_to_group_dto(json_data):
    try:
        group = json_data.get("group") if "group" in json_data else json_data.get("group_id")
        member = json_data.get("admin") if "admin" in json_data else json_data.get("member")

        if not group or not member:
            raise ValueError("Incomplete user data")

        return (True, GroupDTO(group, member))
    except (TypeError, ValueError) as e:
        return (False, f"error when extracting data: {e}")

def group_dto_to_group_entity(group_dto: GroupDTO, admin: bool):
    return Group(group=group_dto.group, member=group_dto.member, admin=admin)

def group_entity_to_group_dto(group: Group):
    return GroupDTO(group=group.group, member=group.member)