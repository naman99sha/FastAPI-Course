from fastapi import APIRouter
from fastapi import Depends, HTTPException, Path
import models
from database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status
from pydantic import BaseModel, Field
from .auth import get_user_verified

app = APIRouter(
    prefix='/todo',
    tags=['todo']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_user_verified)]
        
class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool
        
@app.get("/")
async def read_all(user: user_dependency,db: db_dependency):
    return db.query(models.Todos).filter(models.Todos.owner_id == user.get('id')).all()

@app.get("/{todo_id}", status_code=status.HTTP_200_OK)
async def read_one(user: user_dependency,db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(models.Todos).filter(models.Todos.owner_id==user.get('id')).filter(models.Todos.id == todo_id).first()
    if todo_model:
        return todo_model
    raise HTTPException(status_code=404, detail="Record doesn't exist")

@app.post("/create",status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency,db: db_dependency, todo_request: TodoRequest):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    todo_model = models.Todos(**todo_request.dict(), owner_id = user.get('id'))
    db.add(todo_model)
    db.commit()

@app.put("/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency,db: db_dependency, todo_request: TodoRequest, todo_id : int = Path(gt=0)):
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).filter(models.Todos.owner_id == user.get('id')).first()
    if todo_model:
        todo_model.title = todo_request.title
        todo_model.description = todo_request.description
        todo_model.priority = todo_request.priority
        todo_model.complete = todo_request.complete
        db.add(todo_model)
        db.commit()
    else:
        raise HTTPException(status_code=404, detail="Record not found") 
    
@app.delete("/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency,db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).filter(models.Todos.owner_id == user.get('id')).first()
    if todo_model:
        db.delete(todo_model)
        db.commit()
    else:
        raise HTTPException(status_code=404, detail="Records not found")