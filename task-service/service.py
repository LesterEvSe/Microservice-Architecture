from http.server import BaseHTTPRequestHandler
import json

import logic
from Mappings.mapper import *
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
            self._send_data(logic.get_groups_for_username(data["username"]))
        
        elif msg_type == "is_admin":
            res = logic.json_to_group_dto(data)
            if res[0]:
                self._send_data({"is_admin": logic.is_user_admin_of_group(res[1])})
            else:
                self._send_error(res[1])
        
        elif msg_type == "get_group_users":
            res = json_to_group_dto(data)
            if not res[0]:
                self._send_error(res[1])
                return

            (res, users) = logic.get_group_users(res[1])
            if not res:
                self._send_error(users)
            else:
                self._send_data({"users": users})

        elif msg_type == "add_group":
            res = json_to_group_dto(data)
            if not res[0]:
                self._send_error(res[1])
                return
            
            (res, id) = logic.add_group(res[1])
            if not res:
                self._send_error(id)
            else:
                self._send_data({"group_id" : id})
        
        elif msg_type == "delete_group":
            res = json_to_group_dto(data)
            if not res[0]:
                self._send_error(res[1])
                return
            
            if logic.delete_group(res[1]):
                self._send_error("failed to delete group.")
            else:
                self._send_data({})
        
        elif msg_type == "add_member_to_group":
            res = json_to_group_dto(data)
            if not res[0]:
                self._send_error(res[1])
                return
            
            if logic.add_member_to_group(data["member"], res[1]):
                self._send_error("failed to add member to group.")
            else:
                self._send_data({})
        
        elif msg_type == "delete_member_from_group":
            res = json_to_group_dto(data)
            if not res[0]:
                self._send_error(res[1])
                return
            
            if logic.delete_member_from_group(data["member"], res[1]):
                self._send_error("failed to delete member from group.")
            else:
                self._send_data({})
        
        # Task
        elif msg_type == "add_task":
            res = json_to_task_dto(data)
            if not res:
                self._send_error(res[1])
                return

            (res, id) = logic.add_task(data["user"], data["group_id"], res[1])
            if not res:
                self._send_error(id)
            else:
                self._send_data({"task_id": id})
        
        elif msg_type == "delete_task":
            res = json_to_group_data_dto(data)
            if not res[0]:
                self._send_error(res[1])
                return
            
            err = logic.delete_task(res[1])
            if err:
                self._send_error(err)
            else:
                self._send_data({})
        
        elif msg_type == "update_task":
            task_dto = json_to_task_dto(data)
            if not task_dto[0]:
                self._send_error(task_dto[1])
                return
            
            group_data_dto = json_to_group_data_dto(data)
            if not group_data_dto[0]:
                self._send_error(group_data_dto[1])
                return
            
            err = logic.update_task(group_data_dto[1], task_dto[1])
            if err:
                self._send_error(err)
            else:
                self._send_data({})
        
        
        elif msg_type == "get_tasks_for_group":
            res = json_to_group_dto(data)
            if not res[0]:
                self._send_error(res[1])
                return
            
            (res, tasks) = logic.get_tasks_for_group(res[1])
            if not res:
                self._send_error(tasks)
            else:
                self._send_data(tasks)
        
        elif msg_type == "get_assigned_users_to_task":
            res = json_to_group_data_dto(data)
            if not res[0]:
                self._send_error(res[1])
                return
            
            (res, users) = logic.get_assigned_users_to_task(res[1])
            if not res:
                self._send_error(users)
            else:
                self._send_data(users)
