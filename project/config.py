import os

rabbitmq_url = os.environ.get("RABBITMQ_URL")
mongo_url = os.environ.get("MONGO_DB")

app_port = int(os.environ.get("PORT", "3000"))
mongo_db = os.environ.get("MONGO_DB", "task_runner")

taskRunnerRoutingKey = "task_runner"
exchangeName = "task_runner"
