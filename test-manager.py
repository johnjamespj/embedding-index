import pickle, json

import project.manager.queue as manager
import project.manager.tasks as tasks

import project.queue as queue
from project.queue import getRabbitMQChannel

channel = getRabbitMQChannel()
taskRunnerRoutingKey = "test_result_queue"
channel.queue_declare(queue=taskRunnerRoutingKey, durable=True)

manager.initiateQueue()
taskId = tasks.createTask("image.featureAndFaceEmbedding", taskRunnerRoutingKey, {
    "url": "https://starktimes.com/wp-content/uploads/2021/06/Eva-Elfie.jpg"
})
print(taskId)

def queueMessageCallback(ch, method, properties, body):
    print(pickle.loads(body))
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.queue_declare(queue=taskRunnerRoutingKey, durable=True)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue=taskRunnerRoutingKey, on_message_callback=queueMessageCallback)
channel.start_consuming()
