import os

import RabbitMQ.Configuration as Configuration
from RabbitMQ.RabbitMQConnection import RabbitMQConnection, RabbitMQException

class IncorrectInputException(Exception):
    pass

exchange = os.getenv('RABBITMQ_EXCHANGE_NAME')

class Listener:
    connection = None
    channel = None

    def __init__(self, routing_key, exchange=exchange):
        try:
            self.connection = RabbitMQConnection()

            self.channel = self.connection.channel()
            self.channel.exchange_declare(exchange=exchange, exchange_type='direct')

            queue = Configuration.ROUTING[routing_key]['QUEUE_NAME']

            self.channel.queue_declare(queue=queue)
            self.channel.queue_bind(exchange=exchange, queue=queue, routing_key=routing_key)
        except Exception as e:
            raise RabbitMQException(f"Unable to connect to rabbitMQ {str(e)}") from e

    def run(self):
        self.channel.start_consuming()

    def attachCallbackToQueue(self, queue, callback):
        self.channel.basic_consume(queue=queue,on_message_callback=callback,auto_ack=True)

