from http.server import BaseHTTPRequestHandler
import json
import requests
from db import UserService

TASK_SERVICE=5002
DB = UserService()

class UserHandler(BaseHTTPRequestHandler):
    def _task_service_interaction(self, json_data, jwt=None):
        task_data = json.loads(self.send_to_service(TASK_SERVICE, json_data))

        # task_data["error"] can't do this, because of KeyError
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
        received_data = json.loads(post_data.decode('utf-8'))

        msg_type = received_data["type"]
        if msg_type == "registration":
            jwt_token = DB.register_user(received_data)
            
            if jwt_token[0]:
                self._task_service_interaction(json.dumps({
                    "type": "get_groups",
                    "username": received_data["username"]
                }), jwt_token[1])
            else:
                self._send_error(jwt_token[1])

        # Not implement properly yet
        elif msg_type == "login":
            jwt_token = DB.login_user(received_data)

            if jwt_token:
                self._task_service_interaction(json.dumps({
                    "type": "get_groups",
                    "username": received_data["username"]
                }), jwt_token)
            else:
                self._send_error("Incorrect login or password.")

        #elif msg_type == "add_task":


    def send_to_service(self, to_port, json_data):
        service_url = f'http://localhost:{to_port}/'

        print(json_data)
        try:
            response = requests.post(service_url, headers={'Content-Type': 'application/json'}, data=json_data)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Failed to communicate with service at port {to_port}, status code: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
