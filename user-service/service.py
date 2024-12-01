import pika
import json

import logic
from Data.UserDTO import *
from Data.GoogleDTO import *

'''
{
                                                                 "type": "google_sign_up",
                                                                 "username": "Test0",
                                                                 "jwt": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjM2MjgyNTg2MDExMTNlNjU3NmE0NTMzNzM2NWZlOGI4OTczZDE2NzEiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJhenAiOiIxMDY0MjE3NDM5NzA0LThya2w2MGRlY2lqYWFkZWdoMzU1aHVqMG1uZzgwbnY3LmFwcHMuZ29vZ2xldXNlcmNvbnRlbnQuY29tIiwiYXVkIjoiMTA2NDIxNzQzOTcwNC04cmtsNjBkZWNpamFhZGVnaDM1NWh1ajBtbmc4MG52Ny5hcHBzLmdvb2dsZXVzZXJjb250ZW50LmNvbSIsInN1YiI6IjEwMjYxOTA2MTAxODUzMjE1NzcyMiIsImVtYWlsIjoiZXZnZW5paS5uaWtvbGFldmljaGZnaEBnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwibm9uY2UiOiJzbXRoIiwibmJmIjoxNzMyODc5MjgxLCJpYXQiOjE3MzI4Nzk1ODEsImV4cCI6MTczMjg4MzE4MSwianRpIjoiOTljNzllMzBmOTlhZmYwNjg5YzM3NDY5ZTlmY2RkNjEwYjExNGM2ZSJ9.HuoGqM9pvxvxmJ3e6DA8hz5X57_wNk5L2bgQaNalHmFx9a8ighbjCt2FIQTQITL-gpU6JJj6FmGEplBLu-tvoGeov1RtNzNyqjZWcZEbouRZ2EUXq4Q3xkd1Bz8Rd8EWs5LqhbPYrFq1b286VfkogGUSFqaYIiFsv67Ipm44mRgFp32Thg6QPZpV6ZlcnHPc2Uuq-fWOWPFsWq-75J8OjqYIZYx-4Qxgp1XYetep7DH4ZhICwfmE77dK6bB4UC25gwLAhPpqwx5-woF3_Pn216SYXHsqi77ASBJBwL5l8kzRZHCRlVMT5areR860GYHVbEUfCHv39anIDW20cJjbag"}
'''

class RabbitMQClient:
    def _send_data(self, data: dict, send_to_queue: str, correlation_id, reply_to_queue=None):
        if not send_to_queue.startswith('amq.gen-'):
            self.channel.queue_declare(queue=send_to_queue, durable=True)
        
        self.channel.basic_publish(
            exchange='',
            routing_key=send_to_queue,
            body=json.dumps(data),
            properties=pika.BasicProperties(
                delivery_mode=2, # Saving messages
                reply_to=reply_to_queue,
                correlation_id=correlation_id
            )
        )
        print(f"Sent data to {send_to_queue} with correlation_id {correlation_id}: {data}")
        print("reply to queue", reply_to_queue)

    def _send_error(self, error_msg: str, send_to_queue: str, correlation_id):
        if not send_to_queue.startswith('amq.gen-'):
            self.channel.queue_declare(queue=send_to_queue, durable=True)

        self.channel.basic_publish(
            exchange='',
            routing_key=send_to_queue,
            body=json.dumps({"error" : error_msg}),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Saving messages
                correlation_id=correlation_id
            )
        )
        print(f"Sent error to {send_to_queue} with correlation_id {correlation_id}: {error_msg}")
        
    
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
        print("get message", data)
        msg_type = data["type"]

        reply_to = properties.reply_to
        correlation_id = properties.correlation_id
        if msg_type == "registration":
            user_dto = logic.json_to_user_dto(data)
            if not user_dto[0]:
                self._send_error(user_dto[1], reply_to, correlation_id)
                return
            user_dto = user_dto[1]

            (res, jwt_token) = logic.register_user(user_dto)
            if not res:
                self._send_error(jwt_token, reply_to, correlation_id)
            else:
                self._send_data({"jwt": jwt_token}, reply_to, correlation_id)
            return

        elif msg_type == "login":
            # plug for email, because we don't need it for login
            data["email"] = "plug"
            user_dto = logic.json_to_user_dto(data)
            
            if not user_dto[0]:
                self._send_error(user_dto[1], reply_to, correlation_id)
                return
            user_dto = user_dto[1]

            (res, jwt_token) = logic.login_user(user_dto)
            if not res:
                self._send_error(jwt_token, reply_to, correlation_id)
            else:
                self._send_data({"jwt": jwt_token}, reply_to, correlation_id)
            return
        
        elif msg_type == "google_sign_up":
            (res, google_dto) = logic.json_to_google_dto(data)
            if not res:
                self._send_error(google_dto, reply_to, correlation_id)
                return
            
            (res, jwt_token) = logic.google_sign_up(google_dto)
            if not res:
                self._send_error(jwt_token, reply_to, correlation_id)
            else:
                self._send_data({"jwt": jwt_token}, reply_to, correlation_id)
            return

        check_jwt = logic.get_username_and_check_jwt(data["jwt"])
        if not check_jwt[0]:
            self._send_error(check_jwt[1], reply_to, correlation_id)
            return

        username = check_jwt[1]
        if msg_type == "get_groups":
            self._send_data({
                "type": "get_groups",
                "username": username
            }, self.task_service_queue, correlation_id, reply_to)
        
        elif msg_type == "is_admin":
            self._send_data({
                "type": "is_admin",
                "group_id": data["group_id"],
                "member": username
            }, self.task_service_queue, correlation_id, reply_to)
        
        elif msg_type == "get_group_users":
            self._send_data({
                "type": "get_group_users",
                "group_id": data["group_id"],
                "member": username
            }, self.task_service_queue, correlation_id, reply_to)
        
        elif msg_type == "add_group":
            self._send_data({
                "type": "add_group",
                "group": data["group"],
                "admin": username
            }, self.task_service_queue, correlation_id, reply_to)
        
        elif msg_type == "delete_group":
            self._send_data({
                "type": "delete_group",
                "group_id": data["group_id"],
                "admin": username
            }, self.task_service_queue, correlation_id, reply_to)
        
        elif msg_type == "add_member_to_group":
            if not logic.is_user_exist(data.get("member")):
                self._send_error("member is not exist.", reply_to, correlation_id)
                return
            self._send_data({
                "type": "add_member_to_group",
                "group_id": data["group_id"],
                "member": data["member"],
                "admin": username
            }, self.task_service_queue, correlation_id, reply_to)
        
        elif msg_type == "delete_member_from_group":
            self._send_data({
                "type": "delete_member_from_group",
                "group_id": data["group_id"],
                "member": data["member"],
                "admin": username
            }, self.task_service_queue, correlation_id, reply_to)
        
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
            }, self.task_service_queue, correlation_id, reply_to)
        
        elif msg_type == "delete_task":
            self._send_data({
                "type": "delete_task",
                "group_id": data["group_id"],
                "task_id": data["task_id"],
                "user": username,
            }, self.task_service_queue, correlation_id, reply_to)
        
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
            }, self.task_service_queue, correlation_id, reply_to)
        
        elif msg_type == "get_tasks_for_group":
            self._send_data({
                "type": "get_tasks_for_group",
                "group_id": data["group_id"],
                "member": username,
            }, self.task_service_queue, correlation_id, reply_to)
        
        elif msg_type == "get_assigned_users_to_task":
            self._send_data({
                "type": "get_assigned_users_to_task",
                "group_id": data["group_id"],
                "task_id": data["task_id"],
                "user": username
            }, self.task_service_queue, correlation_id, reply_to)
        
        elif msg_type == "get_tasks_for_user":
            self._send_data({
                "type": "get_tasks_for_user",
                "user": username
            }, self.task_service_queue, correlation_id, reply_to)
