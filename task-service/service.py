from http.server import BaseHTTPRequestHandler
import json
from db import TaskService

# Maybe does not need
USER_SERVICE=5001
DB = TaskService()

class TaskHandler(BaseHTTPRequestHandler):
    def _send_error(self, error_msg):
        self.send_response(500)
        self.end_headers()
        self.wfile.write(json.dumps({
            "error": error_msg
        }).encode('utf-8'))
    
    def _send_data(self, json_data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(json_data).encode('utf-8'))
    
    def do_POST(self):
        post_data = self.rfile.read(int(self.headers['Content-Length']))
        data = json.loads(post_data.decode('utf-8'))

        msg_type = data["type"]
        if msg_type == "get_groups":
            json_data = DB.get_groups_for_user(data["username"])
            if json_data:
                self._send_data(json_data)
            else:
                self._send_error("Something went wrong.")

        elif msg_type == "add_group":
            json_data = DB.add_group(data["group"], data["admin"])
            if json_data:
                self._send_data(json_data)
            else:
                self._send_error("Something went wrong.")
        
        elif msg_type == "delete_group":
            if DB.is_user_admin_of_group(data["admin"], data["group_id"]) and DB.delete_group(data["group_id"]):
                self._send_data({})
            else:
                self._send_error("This user is not a group administrator.")
        
        elif msg_type == "add_member_to_group":
            if DB.is_user_admin_of_group(data["admin"], data["group_id"]) and DB.add_member_to_group(data["member"], data["group_id"]):
                self._send_data({})
            else:
                self._send_error("This user is not a group administrator.")
        
        elif msg_type == "delete_member_from_group":
            if DB.is_user_admin_of_group(data["admin"], data["group_id"]) and DB.delete_member_from_group(data["member"], data["group_id"]):
                self._send_data({})
            else:
                self._send_error("This user is not a group administrator.")
        
        elif msg_type == "add_task":
            if DB.is_user_in_group(data["user"], data["group_id"]) and (task_id := DB.add_task(
                data["group_id"], data["task"], data["deadline"], data["description"], data["todo_task"], data["member"]
            )):
                self._send_data(task_id)
            else:
                self._send_error("This user is not in the group.")
        
        elif msg_type == "delete_task":
            if DB.is_user_in_group(data["user"], data["group_id"]) and DB.delete_task(data["task_id"]):
                self._send_data({})
            else:
                self._send_error("You can't delete this task.")
        
        elif msg_type == "update_task":
            if DB.is_user_in_group(data["user"], data["group_id"]) and DB.update_task(
                data["task_id"], data["task"], data["description"], data["deadline"], data["todo_task"], data["member"]
            ):
                self._send_data({})
            else:
                self._send_error("You can't update this task.")
        
        elif msg_type == "get_tasks_for_group":
            if DB.is_user_in_group(data["user"], data["group_id"]) and (tasks := DB.get_tasks_for_group(data["group_id"])):
                self._send_data(tasks)
            else:
                self._send_error("You can't get tasks for this group")
