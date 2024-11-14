from datetime import datetime

class Task:
    # task is task_name or task_id
    def __init__(self, task, description, deadline: datetime, todo_task: bool, members: list[str]):
        self.task = task
        self.description = description
        self.deadline = deadline
        self.todo_task = todo_task
        self.members = members
    
    def __str__(self):
        return (f"task: {self.task}\n"
            f"description: {self.description}\n"
            f"deadline: {self.deadline}\n"
            f"todo_task: {self.todo_task}\n"
            f"members: {', '.join(self.members)}")
