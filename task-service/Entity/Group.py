class Group:
    # Group Id or Name
    def __init__(self, group: str, member: str, admin: bool):
        self.group = group
        self.member = member
        self.admin = admin