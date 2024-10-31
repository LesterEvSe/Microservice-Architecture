from Data.GroupDTO import *
from Entity.Group import *

def json_to_group_dto(json_data):
    try:
        group_name = json_data.get("group_name")
        member = json_data.get("member") if "member" in json_data else json_data.get("admin")

        if not group_name or not member:
            raise ValueError("Incomplete user data")

        return (True, GroupDTO(group_name, member))
    except (TypeError, ValueError) as e:
        return (False, f"error when extracting data: {e}")

def group_dto_to_group_entity(group_dto: GroupDTO, admin: bool):
    return Group(group_name=group_dto.group_name, member=group_dto.member, admin=admin)

def group_entity_to_group_dto(group: Group):
    return GroupDTO(group_name=group.group_name, member=group.member)