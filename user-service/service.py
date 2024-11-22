#from http.server import BaseHTTPRequestHandler
#import requests
import pika
import json

import logic
from Data.UserDTO import *

#TASK_SERVICE=5002

class RabbitMQClient:
    '''
    def _task_service_interaction(self, json_data):
        task_data = self.send_to_service(TASK_SERVICE, json_data)
        if "error" in task_data:
            self._send_error(task_data["error"])
        else:
            self._send_data_ok(task_data)

    def _send_error(self, error_msg):
        self.send_response(500)
        self.end_headers()
        self.wfile.write(json.dumps({
            "error": error_msg
        }).encode())
    
    def _send_data_ok(self, dict_data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(dict_data).encode('utf-8'))
    
    def send_to_service(self, to_port, json_data):
        service_url = f'http://task-service:{to_port}/'
        try:
            response = requests.post(service_url, headers={'Content-Type': 'application/json'}, data=json_data)

            if response.status_code == 200:
                return response.json()
            else:
                error_message = response.text if response.text else "unexpected error from service"
            return {"error": f"Failed to communicate with service at port {to_port}, status code: {response.status_code}, message: {error_message}"}
        except Exception as e:
            return {"error": str(e)}
    '''
    
    def _send_data(self, data: dict, send_to_queue: str, reply_to_queue=None):
        self.channel.queue_declare(queue=send_to_queue, durable=True)

        self.channel.basic_publish(
            exchange='',
            routing_key=send_to_queue,
            body=json.dumps(data),
            properties=pika.BasicProperties(
                delivery_mode=2, # Saving messages
                reply_to=reply_to_queue
            )
        )
        #print(f"[x] Sent message to {send_to_queue}: {data}")

    def _send_error(self, error_msg: str, send_to_queue: str):
        self.channel.queue_declare(queue=send_to_queue, durable=True)

        self.channel.basic_publish(
            exchange='',
            routing_key=send_to_queue,
            body=json.dumps({"error" : error_msg}),
            properties=pika.BasicProperties(delivery_mode=2)  # Saving messages
        )
        #print(f"[x] Sent message to {send_to_queue}: {error_msg}")
        
    
    def __init__(self, queue_name, host='rabbitmq', port=5672, vhost='/', user='admin', password='password'):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host,
                port,
                vhost,
                pika.PlainCredentials(user, password)
            )
        )
        self.channel = self.connection.channel()
        self.queue_name = queue_name
        self.task_service_queue = 'task_service_queue'
    
    def __del__(self):
        self.connection.close()
    
    def start_consumer(self):
        # Check if queue exist
        self.channel.queue_declare(queue=self.queue_name, durable=True)
        self.channel.basic_consume(
            queue=self.queue_name,
            auto_ack=True,
            on_message_callback=self.process_message
        )
        print(f"[*] Waiting for messages in {self.queue_name}")
        self.channel.start_consuming()

    def process_message(self, ch, method, properties, body):
        data = json.loads(body)
        msg_type = data["type"]

        reply_to = properties.reply_to
        if msg_type == "registration":
            user_dto = logic.json_to_user_dto(data)
            if not user_dto[0]:
                self._send_error(user_dto[1], reply_to)
                return
            user_dto = user_dto[1]

            (res, jwt_token) = logic.register_user(user_dto)
            if not res:
                self._send_error(jwt_token, reply_to)
            else:
                self._send_data({"jwt": jwt_token}, reply_to)
            return

        elif msg_type == "login":
            # plug for email, because we don't need it for login
            data["email"] = "plug"
            user_dto = logic.json_to_user_dto(data)
            
            if not user_dto[0]:
                self._send_error(user_dto[1], reply_to)
                return
            user_dto = user_dto[1]

            (res, jwt_token) = logic.login_user(user_dto)
            if not res:
                self._send_error(jwt_token, reply_to)
            else:
                self._send_data({"jwt": jwt_token}, reply_to)
            return

        check_jwt = logic.get_username_and_check_jwt(data["jwt"])
        if not check_jwt[0]:
            self._send_error(check_jwt[1], reply_to)
            return

        username = check_jwt[1]
        if msg_type == "get_groups":
            self._send_data({
                "type": "get_groups",
                "username": username
            }, self.task_service_queue, reply_to)
        
        elif msg_type == "is_admin":
            self._send_data({
                "type": "is_admin",
                "group_id": data["group_id"],
                "member": username
            }, self.task_service_queue, reply_to)
        
        elif msg_type == "get_group_users":
            self._send_data({
                "type": "get_group_users",
                "group_id": data["group_id"],
                "member": username
            }, self.task_service_queue, reply_to)
        
        elif msg_type == "add_group":
            self._send_data({
                "type": "add_group",
                "group": data["group"],
                "admin": username
            }, self.task_service_queue, reply_to)
        
        elif msg_type == "delete_group":
            self._send_data({
                "type": "delete_group",
                "group_id": data["group_id"],
                "admin": username
            }, self.task_service_queue, reply_to)
        
        elif msg_type == "add_member_to_group":
            if not logic.is_user_exist(data.get("member")):
                self._send_error("member is not exist.", reply_to)
                return
            self._send_data({
                "type": "add_member_to_group",
                "group_id": data["group_id"],
                "member": data["member"],
                "admin": username
            }, self.task_service_queue, reply_to)
        
        elif msg_type == "delete_member_from_group":
            self._send_data({
                "type": "delete_member_from_group",
                "group_id": data["group_id"],
                "member": data["member"],
                "admin": username
            }, self.task_service_queue, reply_to)
        
        elif msg_type == "add_task":
            self._send_data({
                "type": "add_task",
                "group_id": data["group_id"],
                "task_name": data["task_name"],
                "description": data["description"],
                "deadline": data["deadline"],
                "todo_task": data["todo_task"],
                "members": data["members"],  # Array of users
                "user": username,  # The one who adds the task
            }, self.task_service_queue, reply_to)
        
        elif msg_type == "delete_task":
            self._send_data({
                "type": "delete_task",
                "group_id": data["group_id"],
                "task_id": data["task_id"],
                "user": username,
            }, self.task_service_queue, reply_to)
        
        elif msg_type == "update_task":
            self._send_data({
                "type": "update_task",
                "group_id": data["group_id"],
                "task_id": data["task_id"],
                "task_name": data["task_name"],
                "description": data["description"],
                "deadline": data["deadline"],
                "todo_task": data["todo_task"],
                "members": data["members"],
                "user": username,
            }, self.task_service_queue, reply_to)
        
        elif msg_type == "get_tasks_for_group":
            self._send_data({
                "type": "get_tasks_for_group",
                "group_id": data["group_id"],
                "member": username,
            }, self.task_service_queue, reply_to)
        
        elif msg_type == "get_assigned_users_to_task":
            self._send_data({
                "type": "get_assigned_users_to_task",
                "group_id": data["group_id"],
                "task_id": data["task_id"],
                "user": username
            }, self.task_service_queue, reply_to)
