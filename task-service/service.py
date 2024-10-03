from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import requests
from constants import *

class MyHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        post_data = self.rfile.read(int(self.headers['Content-Length']))
        
        # Convert bytes to JSON format
        received_data = json.loads(post_data)

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        # Send response
        response = {"message": "JSON received successfully", "data": received_data}
        self.wfile.write(json.dumps(response).encode())
    
    def send_to_frontend(self, data):
        """Send data back to the FRONTEND server"""
        try:
            frontend_url = f'http://localhost:{FRONTEND}/receive_json'
            print(f"Sending data to FRONTEND at {frontend_url}")
            response = requests.post(frontend_url, json=data)
            
            # Check if response is OK
            if response.status_code == 200:
                return response.json()  # Return JSON response from FRONTEND
            else:
                return {"error": f"Failed to communicate with FRONTEND, status code: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}