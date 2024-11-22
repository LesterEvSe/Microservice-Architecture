from service import RabbitMQClient
from RabbitMQ.producer import *

if __name__ == "__main__":
    client = RabbitMQClient('user_service_queue')
    client.start_consumer()