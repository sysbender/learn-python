from fastapi import FastAPI
from redis import Redis 
from rq import Queue
from pydantic import BaseModel
from job import print_number


app = FastAPI()

redis_conn = Redis( host="192.168.0.30" , port=6379)
task_queue = Queue( "task_queue", connection=redis_conn)


class JobData(BaseModel):
    x: int
    y: int 


@app.get("/")
def index():
    return {
        "success" : True, 
        "message" : "pong"

    }

@app.post("/job")
def post_job(job_data : JobData):
    x = job_data.x
    y = job_data.y
    job_instance = task_queue.enqueue(print_number, x, y)
    return {
        "success" : True, 
        "job_id" : job_instance.id
    }



