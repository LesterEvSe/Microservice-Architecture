class Group:
    def __init__(self, group_name: str, member: str, admin: bool):
        self.group_name = group_name
        self.member = member
        self.admin = admin