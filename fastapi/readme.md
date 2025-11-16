

* https://www.youtube.com/watch?v=Lw-zLopB3o0&list=PL-2EBeDYMIbQghmnb865lpdmYyWU3I5F1&index=1
* https://www.youtube.com/watch?v=7t2alSnE2-I
* Udemy - FastAPI - The Complete Course (Beginner + Advanced)  


## install  

```shell

pip install "uvicorn[standard]"
 pip install "fastapi[standard]"

uvicorn main:app --reload  # application:
fastapi run main.py
fastapi dev main.py

```

CRUD operation , swagger UI
create - POST
read - GET
update - PUT
delete - DELETE

## path parameter 

```python 

# static path parameter


# dynamic path parameter
@app.get("/book/{dynamic_param}")
async def read_all_books(dynamic_param):
    return {'dynamic_param': dynamic_param}

```
