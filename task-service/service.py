#from http.server import BaseHTTPRequestHandler
import pika
import json

import logic
from Mappings.mapper import *
from Data.GroupDTO import *


class RabbitMQClient:
    '''
    def _send_error(self, error_msg):
        self.send_response(500)
        self.end_headers()
        self.wfile.write(error_msg.encode('utf-8'))
    
    def _send_data(self, dict_data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(dict_data).encode('utf-8'))
    '''
    
    def _send_data(self, dict_data: dict, queue_name, correlation_id):
        self.channel.queue_declare(queue=queue_name, durable=True)

        self.channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps(dict_data),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Saving messages
                correlation_id=correlation_id
            )
        )
        #print(f"[x] Sent message to {queue_name}: {message}")

    def _send_error(self, error_msg: str, queue_name, correlation_id):
        self.channel.queue_declare(queue=queue_name, durable=True)

        self.channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps({"error" : error_msg}),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Saving messages
                correlation_id=correlation_id
            )
        )
        #print(f"[x] Sent message to {queue_name}: {err_message}")
        
    
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
        correlation_id = properties.correlation_id
        if msg_type == "get_groups":
            self._send_data(logic.get_groups_for_username(data["username"]), reply_to, correlation_id)
        
        elif msg_type == "is_admin":
            res = logic.json_to_group_dto(data)
            if res[0]:
                self._send_data({"is_admin": logic.is_user_admin_of_group(res[1])}, reply_to, correlation_id)
            else:
                self._send_error(res[1], reply_to, correlation_id)
        
        elif msg_type == "get_group_users":
            res = json_to_group_dto(data)
            if not res[0]:
                self._send_error(res[1], reply_to, correlation_id)
                return

            (res, users) = logic.get_group_users(res[1])
            if not res:
                self._send_error(users, reply_to, correlation_id)
            else:
                self._send_data({"users": users}, reply_to, correlation_id)

        elif msg_type == "add_group":
            res = json_to_group_dto(data)
            if not res[0]:
                self._send_error(res[1], reply_to, correlation_id)
                return
            
            (res, id) = logic.add_group(res[1])
            if not res:
                self._send_error(id, reply_to, correlation_id)
            else:
                self._send_data({"group_id" : id}, reply_to, correlation_id)
        
        elif msg_type == "delete_group":
            res = json_to_group_dto(data)
            if not res[0]:
                self._send_error(res[1], reply_to, correlation_id)
                return
            
            if logic.delete_group(res[1]):
                self._send_error("failed to delete group.", reply_to, correlation_id)
            else:
                self._send_data({}, reply_to, correlation_id)
        
        elif msg_type == "add_member_to_group":
            res = json_to_group_dto(data)
            if not res[0]:
                self._send_error(res[1], reply_to, correlation_id)
                return
            
            if logic.add_member_to_group(data["member"], res[1]):
                self._send_error("failed to add member to group.", reply_to, correlation_id)
            else:
                self._send_data({}, reply_to, correlation_id)
        
        elif msg_type == "delete_member_from_group":
            res = json_to_group_dto(data)
            if not res[0]:
                self._send_error(res[1], reply_to, correlation_id)
                return
            
            if logic.delete_member_from_group(data["member"], res[1]):
                self._send_error("failed to delete member from group.", reply_to, correlation_id)
            else:
                self._send_data({}, reply_to, correlation_id)
        
        # Task
        elif msg_type == "add_task":
            res = json_to_task_dto(data)
            if not res:
                self._send_error(res[1], reply_to, correlation_id)
                return

            (res, id) = logic.add_task(data["user"], data["group_id"], res[1])
            if not res:
                self._send_error(id, reply_to, correlation_id)
            else:
                self._send_data({"task_id": id}, reply_to, correlation_id)
        
        elif msg_type == "delete_task":
            res = json_to_group_data_dto(data)
            if not res[0]:
                self._send_error(res[1], reply_to, correlation_id)
                return
            
            err = logic.delete_task(res[1])
            if err:
                self._send_error(err, reply_to, correlation_id)
            else:
                self._send_data({}, reply_to, correlation_id)
        
        elif msg_type == "update_task":
            task_dto = json_to_task_dto(data)
            if not task_dto[0]:
                self._send_error(task_dto[1], reply_to, correlation_id)
                return
            
            group_data_dto = json_to_group_data_dto(data)
            if not group_data_dto[0]:
                self._send_error(group_data_dto[1], reply_to, correlation_id)
                return
            
            err = logic.update_task(group_data_dto[1], task_dto[1])
            if err:
                self._send_error(err, reply_to, correlation_id)
            else:
                self._send_data({}, reply_to, correlation_id)
        
        
        elif msg_type == "get_tasks_for_group":
            res = json_to_group_dto(data)
            if not res[0]:
                self._send_error(res[1], reply_to, correlation_id)
                return
            
            (res, tasks) = logic.get_tasks_for_group(res[1])
            if not res:
                self._send_error(tasks, reply_to, correlation_id)
            else:
                self._send_data(tasks, reply_to, correlation_id)
        
        elif msg_type == "get_assigned_users_to_task":
            res = json_to_group_data_dto(data)
            if not res[0]:
                self._send_error(res[1], reply_to, correlation_id)
                return
            
            (res, users) = logic.get_assigned_users_to_task(res[1])
            if not res:
                self._send_error(users, reply_to, correlation_id)
            else:
                self._send_data(users, reply_to, correlation_id)
