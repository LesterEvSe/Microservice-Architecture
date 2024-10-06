from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import requests
from db import TaskService

# Maybe does not need``
USER_SERVICE=5001

DB = TaskService()

class MyHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        post_data = self.rfile.read(int(self.headers['Content-Length']))
        
        # Convert bytes to JSON format
        received_data = json.loads(post_data)
        print(received_data)

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        # Send response
        response = {"message": "JSON received successfully", "data": received_data}
        self.wfile.write(json.dumps(response).encode())
