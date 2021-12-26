import pika, pickle

from project.queue import channel
from project.logging import logger
from project.config import taskRunnerRoutingKey

def initiateQueue():
    logger.info("Initiating task runner queue")
    channel.queue_declare(queue=taskRunnerRoutingKey, durable=True)

def addMessageToQueue(message, queue=taskRunnerRoutingKey):
    channel.basic_publish(
        exchange='',
        routing_key=queue,
        body=pickle.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
        )
    )

def cleanUp():
    logger.info("task runner closing")
    connection.close()