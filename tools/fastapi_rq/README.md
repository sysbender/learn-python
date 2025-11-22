

```shell
uv run uvicorn main:app --reload


rq worker task_queue --url redis://192.168.0.30:6379 --worker-class rq.worker.SimpleWorker


```