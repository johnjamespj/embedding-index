import multiprocessing as mp
from importlib import reload

def startWorker():
    import project.worker.queue as worker
    worker = reload(worker)
    worker.startWorker()

# delete workers
# pool.terminate(), pool.join()
# keyboard interrupt (KeyboardInterrupt)
def startWorkers(nWorkers=2):
    pool = mp.Pool(processes=nWorkers)
    for i in range(0, nWorkers):
        pool.apply_async(startWorker)
    return pool
