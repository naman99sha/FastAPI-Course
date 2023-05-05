from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()

class Book(BaseModel):
    id: int
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=5)
    rating: int = Field(gt=0, lte=5)

Books = [
    {'title':'Title One','author':'Author One','category':'Category One'},
    {'title':'Title Two','author':'Author Two','category':'Category Two'},
    {'title':'Title Three','author':'Author Three','category':'Category Three'},
    {'title':'Title Four','author':'Author Four','category':'Category Four'},
    {'title':'Title Five','author':'Author Five','category':'Category Five'},
    {'title':'Title Six','author':'Author Six','category':'Category Six'},
]
@app.get("/books")
async def read_all_books():
    return Books

@app.get("/books/{book_title}")
async def get_book(book_title: str):
    for book in Books:
        if book.get('title').casefold() == book_title.casefold():
            return book
        
@app.post("/book/create_book")
async def create_book(new_book: Book):
    Books.append(new_book)