import tasks.sample as sample

tasks = {
    "sample.test": sample.test
}

def process(payload):
    name = payload["$name"]
    return tasks[name](payload)
