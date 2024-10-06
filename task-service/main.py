from service import *

CURR_SERVICE = 5002

if __name__ == "__main__":
    server_address = ('', CURR_SERVICE)
    httpd = HTTPServer(server_address, MyHandler)
    print(f"Starting service on port {CURR_SERVICE}...")
    httpd.serve_forever()
