class GroupData:
    def __init__(self, group_id, task_id, user):
        self.group_id = group_id
        self.task_id = task_id
        self.user = user
    
    def __str__(self):
        return f"group_id: {self.group_id}\ntask_id: {self.task_id}\nuser: {self.user}"