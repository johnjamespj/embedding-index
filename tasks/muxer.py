import tasks.sample as sample
import tasks.image as image

tasks = {
    "sample.test": sample.test,
    "image.featureAndFaceEmbedding": image.featureAndFaceEmbedding,
    "image.faceEmbedding": image.faceEmbedding,
    "image.featureEmbedding": image.featureEmbedding
}

def process(payload):
    name = payload["$name"]
    return tasks[name](payload)
