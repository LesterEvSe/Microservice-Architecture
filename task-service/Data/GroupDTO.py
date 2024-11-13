class GroupDTO:
    # Group Id or Name
    def __init__(self, group, member: str):
        self.group = group
        self.member = member
    def __str__(self):
        return f"Group: {self.group}, Member: {self.member}"