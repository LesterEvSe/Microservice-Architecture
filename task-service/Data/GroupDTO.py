class GroupDTO:
    # self.group is group_id or group_name
    def __init__(self, group, member: str):
        self.group = group
        self.member = member
    
    def __str__(self):
        return f"Group: {self.group}, Member: {self.member}"