import os
from redis import Redis
from rq import Queue
from rq.worker import SimpleWorker  # 1. Import the class

# Configure Redis connection
redis_url = 'redis://192.168.0.30:6379'
conn = Redis.from_url(redis_url)

listen = ['task_queue']
# 2. Create Queue objects with the explicit connection
queues = [Queue(name, connection=conn) for name in listen]

if __name__ == '__main__':
    # 3. Instantiate SimpleWorker directly (do NOT use 'Worker')
    worker = SimpleWorker(queues, connection=conn)
    
    print(f"Listening on {listen}...")
    worker.work()