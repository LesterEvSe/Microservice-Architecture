import pika
import json
import os

def process_message(ch, method, properties, body):
    message = json.loads(body)
    print(f"[x] Received message: {message}")
    
    # Логіка обробки повідомлення
    response = {
        "status": "success",
        "result": "message processed"
    }
    
    # Відправка відповіді назад
    if properties.reply_to:
        # Вказуємо на яку чергу надіслати відповідь
        response_queue = properties.reply_to
        correlation_id = properties.correlation_id
        
        # Відправка відповіді на чергу
        ch.basic_publish(
            exchange='',
            routing_key=response_queue,
            properties=pika.BasicProperties(
                reply_to=properties.reply_to,
                correlation_id=correlation_id
            ),
            body=json.dumps(response)
        )
        print(f"[*] Sent response: {response}")

    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_consumer(queue_name):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            'rabbitmq', 
            5672,   # RabbitMQ port
            '/',    # Virtual host
            pika.PlainCredentials('admin', 'password')
        )
    )
    channel = connection.channel()
    
    # Переконатись, що черга існує
    channel.queue_declare(queue=queue_name, durable=True)

    # Споживаємо повідомлення з черги
    channel.basic_consume(queue=queue_name, on_message_callback=process_message)
    
    print(f"[*] Waiting for messages in {queue_name}")
    channel.start_consuming()
