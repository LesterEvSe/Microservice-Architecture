import pika
import json

def send_message(queue_name: str, message: dict, reply_to_queue: str = None):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            'rabbitmq', 
            5672,   # RabbitMQ port
            '/',    # Virtual host
            pika.PlainCredentials('admin', 'password')
        )
    )
    channel = connection.channel()

    properties = pika.BasicProperties(
        delivery_mode=2,  # Якщо потрібно збереження повідомлення
    )
    
    if reply_to_queue:
        # Додаємо параметр 'reply_to', якщо потрібно
        properties.reply_to = reply_to_queue

    # Відправка повідомлення
    channel.basic_publish(
        exchange='',
        routing_key=queue_name,
        body=json.dumps(message),
        properties=properties
    )
    print(f"[x] Sent message to {queue_name}: {message}")
    connection.close()
