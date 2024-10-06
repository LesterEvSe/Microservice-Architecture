from http.server import HTTPServer
from service import UserHandler

USER_SERVICE=5001

if __name__ == "__main__":
    server_address = ('', USER_SERVICE)
    httpd = HTTPServer(server_address, UserHandler)
    print(f"Starting service on port {USER_SERVICE}...")
    httpd.serve_forever()
