from http.server import HTTPServer
from service import TaskHandler
from RabbitMQ.consumer import *

TASK_SERVICE=5002

if __name__ == "__main__":
    start_consumer('task_service_queue')

    '''
    server_address = ('', TASK_SERVICE)
    httpd = HTTPServer(server_address, TaskHandler)
    print(f"Starting service on port {TASK_SERVICE}...")
    httpd.serve_forever()
    '''