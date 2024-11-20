from http.server import HTTPServer
from service import UserHandler
from RabbitMQ.consumer import *
from RabbitMQ.producer import *

USER_SERVICE=5001

if __name__ == "__main__":
    msg = {
        "type": "get_groups",
        "username": "temp"
    }
    send_message('task_service_queue', msg, reply_to_queue="task_service_queue")
    start_consumer('user_service_queue')

    '''
    server_address = ('', USER_SERVICE)
    httpd = HTTPServer(server_address, UserHandler)
    print(f"Starting service on port {USER_SERVICE}...")
    httpd.serve_forever()
    '''