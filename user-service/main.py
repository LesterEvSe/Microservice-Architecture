from service import RabbitMQClient

if __name__ == "__main__":
    client = RabbitMQClient('user_service_queue')
    client.start_consumer()