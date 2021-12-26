import time, sys, traceback, pika, pickle

from project.queue import getRabbitMQChannel
from project.config import taskRunnerRoutingKey
from tasks.muxer import process

def startWorker():
    initiateQueue()

def initiateQueue():
    channel = getRabbitMQChannel()
    channel.queue_declare(queue=taskRunnerRoutingKey, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=taskRunnerRoutingKey, on_message_callback=queueMessageCallback)
    channel.start_consuming()

channel = getRabbitMQChannel()

def queueMessageCallback(ch, method, properties, body):
    payload = pickle.loads(body)
    result = None
    error = None

    start_time = time.time()
    try:
        result = process(payload)
    except Exception as e:
        # Get current system exception
        ex_type, ex_value, ex_traceback = sys.exc_info()

        # Extract unformatter stack traces as tuples
        trace_back = traceback.extract_tb(ex_traceback)

        # Format stacktrace
        stack_trace = list()

        for trace in trace_back:
            stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))

        error = {
            "type": ex_type.__name__,
            "message": ex_value,
            "stack_trace": stack_trace
        }
    
    print("Task completed %s" % payload["$taskId"])
    ch.basic_publish(
        exchange='',
        routing_key=payload["$resultQueue"],
        body=pickle.dumps({
            "error": error,
            "result": result,
            "time_taken": time.time() - start_time
        }),
        properties=pika.BasicProperties(
            delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
        )
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)
