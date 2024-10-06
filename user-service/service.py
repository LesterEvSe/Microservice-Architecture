from http.server import BaseHTTPRequestHandler
import json
import requests
from db import UserService

TASK_SERVICE=5002
DB = UserService()

'''
curl -X POST http://localhost:5001/ -H "Content-Type: application/json" -d '{
    "type": "registration",
    "username": "Test0",
    "password": "1111",
    "email": "test0@example.com"
}'
'''

class UserHandler(BaseHTTPRequestHandler):
    def _task_service_interaction(self, json_data):
        task_data = self.send_to_service(TASK_SERVICE, json_data)
        if "error" in task_data:
            self._send_error(task_data)
        else:
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
        # TODO test later
        post_data = self.rfile.read(int(self.headers['Content-Length']))
        received_data = json.loads(post_data.decode('utf-8'))
        print(f"Received DATA1 from frontend: {received_data}")

        msg_type = received_data["type"]
        if msg_type == "registration":
            if DB.register_user(received_data):
                self._task_service_interaction(json.dumps({
                    "type": "get_groups",
                    "username": received_data["username"]
                }))
            else:
                self._send_error("This username is already taken.")

        elif msg_type == "login":
            if DB.login_user(received_data):
                self._task_service_interaction(received_data)
            else:
                self._send_error("Incorrect login or password.")

        #elif msg_type == "add_task":


    def send_to_service(self, to_port, data):
        try:
            service_url = f'http://localhost:{to_port}/receive_json'
            print(f"Sending data to service at {service_url}")
            response = requests.post(service_url, json=data)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Failed to communicate with service at port {to_port}, status code: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
