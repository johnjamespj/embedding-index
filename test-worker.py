import project.worker.farm as farm
import project.worker.queue as queue

pool = farm.startWorkers()
# queue.startWorker()
try:
    while True:
        continue
except KeyboardInterrupt:
    pool.terminate()
    pool.join()