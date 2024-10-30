from http.server import BaseHTTPRequestHandler
import json
import requests
import logic
from Data.UserDTO import *

TASK_SERVICE=5002

class UserHandler(BaseHTTPRequestHandler):
    def _task_service_interaction(self, json_data, jwt=None):
        task_data = self.send_to_service(TASK_SERVICE, json_data)
        if "error" in task_data:
            print(task_data)
            self._send_error(task_data["error"])
            return

        if jwt is not None:
            task_data["jwt"] = jwt
        self._send_data_ok(task_data)

    def _send_error(self, error_msg):
        self.send_response(500)
        self.end_headers()
        self.wfile.write(json.dumps({
            "type": "error",
            "message": error_msg
        }).encode())
    
    def _send_data_ok(self, json_data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(json_data).encode('utf-8'))

    def do_POST(self):
        # Get data from other services
        post_data = self.rfile.read(int(self.headers['Content-Length']))
        data = json.loads(post_data.decode('utf-8'))

        msg_type = data["type"]

        if msg_type == "registration":
            user_dto = logic.json_to_user_dto(data)
            if not user_dto[0]:
                self._send_error(user_dto[1])
                return
            user_dto = user_dto[1]

            jwt_token = logic.register_user(user_dto)
            if jwt_token[0]:
                self._task_service_interaction(json.dumps({
                    "type": "get_groups",
                    "username": user_dto.username
                }), jwt_token[1])
            else:
                self._send_error(jwt_token[1])
            return

        elif msg_type == "login":
            # plug for email, because we don't need it for login
            data["email"] = "plug"
            user_dto = logic.json_to_user_dto(data)
            
            if not user_dto[0]:
                self._send_error(user_dto[1])
                return
            user_dto = user_dto[1]

            jwt_token = logic.login_user(user_dto)
            if jwt_token:
                self._task_service_interaction(json.dumps({
                    "type": "get_groups",
                    "username": user_dto.username
                }), jwt_token)
            else:
                self._send_error("Incorrect login or password.")
            return

        check_jwt = logic.get_username_and_check_jwt(msg_type["jwt"])
        if not check_jwt[0]:
            self._send_error(check_jwt[1])
            return

        username = check_jwt[1]
        if msg_type == "add_group":
            self._task_service_interaction(json.dumps({
                "type": "add_group",
                "group": data["group"],
                "admin": username
            }))
        
        elif msg_type == "delete_group":
            self._task_service_interaction(json.dumps({
                "type": "delete_group",
                "group_id": data["group_id"],
                "admin": username
            }))
        
        elif msg_type == "add_member_to_group":
            self._task_service_interaction(json.dumps({
                "type": "add_member_to_group",
                "group_id": data["group_id"],
                "member": data["member"],
                "admin": username
            }))
        
        elif msg_type == "delete_member_from_group":
            self._task_service_interaction(json.dumps({
                "type": "add_member_to_group",
                "group_id": data["group_id"],
                "member": data["member"],
                "admin": username
            }))
        
        elif msg_type == "add_task":
            self._task_service_interaction(json.dumps({
                "type": "add_task",
                "group_id": data["group_id"],
                "task": data["task"],
                "description": data["description"],
                "deadline": data["deadline"],
                "todo_task": data["todo_task"],
                "member": data["member"],  # Can be array of users
                "user": username,  # The one who adds the task
            }))
        
        elif msg_type == "delete_task":
            self._task_service_interaction(json.dumps({
                "type": "delete_task",
                "group_id": data["group_id"],
                "task_id": data["task_id"],
                "user": username,
            }))
        
        elif msg_type == "update_task":
            self._task_service_interaction(json.dumps({
                "type": "update_task",
                "group_id": data["group_id"],
                "task_id": data["task_id"],
                "task": data["task"],
                "description": data["description"],
                "deadline": data["deadline"],
                "todo_task": data["todo_task"],
                "member": data["member"],
                "user": username,
            }))
        
        elif msg_type == "get_tasks_for_group":
            self._task_service_interaction(json.dumps({
                "type": "add_task",
                "group_id": data["group_id"],
                "user": username,
            }))


    def send_to_service(self, to_port, json_data):
        service_url = f'http://task-service:{to_port}/'
        try:
            response = requests.post(service_url, headers={'Content-Type': 'application/json'}, data=json_data)

            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Failed to communicate with service at port {to_port}, status code: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
