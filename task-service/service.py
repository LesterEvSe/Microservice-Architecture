from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from db import TaskService

# Maybe does not need``
USER_SERVICE=5001

DB = TaskService()

class TaskHandler(BaseHTTPRequestHandler):
    def _send_error(self, error_msg):
        self.send_response(500)
        self.end_headers()
        self.wfile.write(json.dumps({
            "type": "error",
            "message": error_msg
        }).encode())
    
    def _send_data(self, json_data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(json_data).encode('utf-8'))
    
    def do_POST(self):
        post_data = self.rfile.read(int(self.headers['Content-Length']))
        received_data = json.loads(post_data.decode('utf-8'))

        msg_type = received_data["type"]
        if msg_type == "get_groups":
            json_data = DB.get_groups_for_user(received_data["username"])
            if "error" in json_data:
                self._send_error(json_data['error'])
            else:
                self._send_data(json_data)
        
