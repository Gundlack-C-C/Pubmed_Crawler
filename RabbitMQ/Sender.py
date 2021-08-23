from RabbitMQ.RabbitMQConnection import RabbitMQConnection
import os
import json

exchange = os.getenv('RABBITMQ_EXCHANGE_NAME')


def sendMessage(message, routing_key, exchange=exchange):
    channel = RabbitMQConnection().channel()
    channel.exchange_declare(exchange=exchange, exchange_type='direct')
    channel.basic_publish(
        exchange=exchange,
        routing_key=routing_key,
        body=json.dumps(message)
    )
    channel.close()
