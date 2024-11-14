from http.server import BaseHTTPRequestHandler
import json

from logic import *
from Data.GroupDTO import *


class TaskHandler(BaseHTTPRequestHandler):
    def _send_error(self, error_msg):
        self.send_response(500)
        self.end_headers()
        self.wfile.write(error_msg.encode('utf-8'))
    
    def _send_data(self, dict_data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(dict_data).encode('utf-8'))
    
    def do_POST(self):
        post_data = self.rfile.read(int(self.headers['Content-Length']))
        data = json.loads(post_data.decode('utf-8'))

        msg_type = data["type"]
        if msg_type == "get_groups":
            self._send_data(get_groups_for_username(data["username"]))
        
        elif msg_type == "is_admin":
            res = json_to_group_dto(data)
            if res[0]:
                self._send_data({"is_admin": is_user_admin_of_group(res[1])})
            else:
                self._send_error(res[1])
        
        # TODO not implemented now
        elif msg_type == "get_group_users":
            res = json_to_group_dto(data)
            if not res[0]:
                self._send_error(res[1])
                return

            (res, users) = get_group_users(res[1])
            if not res:
                self._send_error(users)
            else:
                self._send_data({"users": users})

        elif msg_type == "add_group":
            res = json_to_group_dto(data)
            if not res[0]:
                self._send_error(res[1])
                return
            
            (res, id) = add_group(res[1])
            if not res:
                self._send_error(id)
            else:
                self._send_data({"group_id" : id})
        
        elif msg_type == "delete_group":
            res = json_to_group_dto(data)
            if not res[0]:
                self._send_error(res[1])
                return
            
            if not delete_group(res[1]):
                self._send_error("failed to delete group.")
            else:
                self._send_data({})
        
        # TODO need to test
        elif msg_type == "add_member_to_group":
            res = json_to_group_dto(data)
            if not res[0]:
                self._send_error(res[1])
                return
            
            if not add_member_to_group(data["member"], res[1]):
                self._send_error("failed to delete group.")
            else:
                self._send_data({})
        
        # TODO need to test
        elif msg_type == "delete_member_from_group":
            res = json_to_group_dto(data)
            if not res[0]:
                self._send_error(res[1])
                return
            
            if not delete_member_from_group(data["member"], res[1]):
                self._send_error("failed to delete group.")
            else:
                self._send_data({})
        
        elif msg_type == "add_task":
            res = json_to_group_dto(data)
            if res[0]:
                self._send_data(add_member_to_group(data["member"], res[1]))
            else:
                self._send_error(res[1])
            
            '''
            if DB.is_user_in_group(data["user"], data["group_id"]) and (task_id := DB.add_task(
                data["group_id"], data["task"], data["deadline"], data["description"], data["todo_task"], data["member"]
            )):
                self._send_data(task_id)
            else:
                self._send_error("This user is not in the group.")
            '''
        
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
        
        elif msg_type == "get_assigned_users_to_task":
            pass
