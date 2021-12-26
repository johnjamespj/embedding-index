import pymongo
import numpy as np

import project.config as config

mongo_url = config.mongo_url
mongo_db = config.mongo_db

def getMongoClient():
    client = pymongo.MongoClient(mongo_url)
    return client

client = getMongoClient()
db = client[mongo_db]

def saveEmbeddingIndexes(indexEmbeddingName, embeddings):
    coll = db['%s-embs' % indexEmbeddingName]
    docs = []
    for embedding in embeddings:
        entityId, embedding, doc = embedding
        docs.append({
            "entityId": entityId,
            "embedding": embedding,
            "doc": doc
        })
    coll.insert_many(docs)

def getAllEmbedding(indexEmbeddingName):
    coll = db['%s-embs' % indexEmbeddingName]
    docs = list(coll.find({}, { "embedding": 1, "_id": 0 }))

    embeddings = []
    for doc in docs:
        embeddings.append(np.array(doc["embedding"], dtype=np.float32))

    return np.asarray(embeddings)
