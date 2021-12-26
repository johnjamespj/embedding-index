import uuid

import project.manager.queue as manager
from tasks.muxer import tasks

def createTask(name, resultQueue, payload):
    if name not in tasks:
        return None

    taskId = str(uuid.uuid4())
    manager.addMessageToQueue({
        "$name": name,
        "$resultQueue": resultQueue,
        "$taskId": taskId,
        "payload": payload
    })
    return taskId

def createResultQueue(queue):
    channel.queue_declare(queue=queue, durable=True)
