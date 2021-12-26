import pika

from project.logging import logger
import project.config as config

# todo: add logging for authentication error and invalid
#   rabbitMQ host url
def getRabbitMQChannel():
    logger.info("Connecting to RabbitMQ")
    params = pika.URLParameters(config.rabbitmq_url)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    logger.info("Connection and channel created to RabbitMQ")
    return channel

channel = getRabbitMQChannel()