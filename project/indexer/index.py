import pickle, time, faiss, json

import project.manager.tasks as tasks
import project.indexer.mongo as mongo

from project.queue import getRabbitMQChannel

def basicFaceEmbeddingTaskCreatorCallback(doc, taskRunnerRoutingKey):
    return tasks.createTask("image.faceEmbedding", taskRunnerRoutingKey, {
        "url": doc["imgUrl"]
    })

def basicFaceEmbeddingResultProcessorCallback(res, embeddingStore):
    if res["result"] is None:
        return

    faces = res["result"]["faceEmbedding"]
    taskId = res["$taskId"]

    
    if len(faces) == 1:
        embeddingStore[taskId]["embedding"] = faces[0]["embedding"].tolist()
        return embeddingStore[taskId]

    # multiple ppl in a picture
    doc = embeddingStore[taskId]["doc"]
    entityId = embeddingStore[taskId]["entityId"]
    del embeddingStore[taskId]

    for i in range(0, len(faces)):
        embeddingStore['%s-{%s}' % (taskId, str(i))] = {
            "doc": doc,
            "embedding": faces[i]["embedding"].tolist(),
            "entityId": entityId
        }

# doc should have id and imgUrl
def addToIndex(indexName, docs, taskCreaterCallback=basicFaceEmbeddingTaskCreatorCallback, taskResultProcessorCallback=basicFaceEmbeddingResultProcessorCallback):
    channel = getRabbitMQChannel()
    taskRunnerRoutingKey = "addToIndex_%s_results_%s" % (indexName, str(time.time()))
    channel.queue_declare(queue=taskRunnerRoutingKey, durable=True)
    
    count = len(docs)
    embeddingStore = {}
    for doc in docs:
        taskId = taskCreaterCallback(doc, taskRunnerRoutingKey)
        embeddingStore[taskId] = {
            "doc": doc,
            "entityId": doc["id"]
        }

    docs = []
    processedCount = {
        "count": 0
    }
    def callback(ch, method, properties, body):
        result = pickle.loads(body)
        print("added %s" % result["$taskId"])
        taskResultProcessorCallback(result, embeddingStore)
        ch.basic_ack(delivery_tag=method.delivery_tag)

        processedCount["count"] += 1
        if processedCount["count"] == count:
            ch.stop_consuming()
    
    channel.queue_declare(queue=taskRunnerRoutingKey, durable=True)
    channel.basic_qos(prefetch_count=20)
    channel.basic_consume(queue=taskRunnerRoutingKey, on_message_callback=callback)
    channel.start_consuming()
    mongo.saveEmbeddingIndexes(indexName, list(embeddingStore.values()))

def addToIndexFromJsonFile(filename, indexName):
    n = 20
    with open(filename) as jsonFp:
        data = json.load(jsonFp)
        for i in range(0, len(data), n):
            addToIndex(indexName, data[i:i + n])
        
