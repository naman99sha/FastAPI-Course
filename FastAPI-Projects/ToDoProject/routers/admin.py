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
    prefix='/admin',
    tags=['admin']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_user_verified)]

@app.get("/todo",status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user == None or user.get('role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return db.query(models.Todos).all()

@app.delete("/todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency,db: db_dependency, todo_id: int = Path(gt=0)):
    if user == None or user.get('role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    if todo_model:
        db.delete(todo_model)
        db.commit()
    else:
        raise HTTPException(status_code=404, detail="Records not found")