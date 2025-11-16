# Import the FastAPI class from the fastapi package
from fastapi import FastAPI  # root object



# Create an instance of the FastAPI class
app = FastAPI()

BOOKS = [
    {'title': 'Title One', 'author':'Author One', 'category':'science'}, 
    {'title': 'Title Two', 'author':'Author Two', 'category':'science'}, 
    {'title': 'Title Three', 'author':'Author Three', 'category':'history'}, 
    {'title': 'Title Four', 'author':'Author Four', 'category':'math'}, 
    {'title': 'Title Five', 'author':'Author Five', 'category':'math'}, 
    {'title': 'Title Six', 'author':'Author Two', 'category':'math'}, 
]

# Define a route using a decorator
# This route responds to GET requests sent to the root URL "/"
@app.get("/")  
async def index():
    # Return a dictionary that FastAPI will convert to JSON automatically
    # Note: Use a dictionary, not a set. {"hello": "world"} is valid.
    return {"hello": "world"}

@app.get("/api-endpoint")
async def first_api():
    return {'message': 'Hello FastAPI!'}
@app.get('/books')
async def read_all_books():
    return BOOKS

@app.get("/books/{book_title}")
async def read_book(book_title: str):
    for book in BOOKS:
        if book.get('title').casefold() ==  book_title.casefold():
            return book