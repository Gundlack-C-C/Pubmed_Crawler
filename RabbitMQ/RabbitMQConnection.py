import pika
import os

class RabbitMQException(Exception):
    pass

class RabbitMQConnection(object):
    _instance = None

    def __new__(cls):
        if cls._instance is None or cls._instance.is_closed:
            cls._instance = super(RabbitMQConnection, cls).__new__(cls)
            cls._instance = cls.__connect(cls)
        return cls._instance

    def __connect(cls):
        IP = cls.__getEnvironmentVariable('RABBITMQ_SERVICE_IP')
        PORT = cls.__getEnvironmentVariable('RABBITMQ_SERVICE_PORT')
        username = cls.__getEnvironmentVariable('RABBITMQ_USERNAME')
        password = cls.__getEnvironmentVariable('RABBITMQ_PASSWORD')

        creds = pika.PlainCredentials(username, password)
        parameters = pika.ConnectionParameters(IP, PORT, credentials=creds)

        connection = pika.BlockingConnection(parameters)
        return connection

    def __getEnvironmentVariable(key):
        variable = os.getenv(key)
        if variable is None:
            raise RabbitMQException(f'Environment variable [{key}] does not exist !')
        return variable