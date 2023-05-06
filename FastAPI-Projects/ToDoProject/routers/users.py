from fastapi import APIRouter
from fastapi import Depends, HTTPException, Path
import models
from database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status
from pydantic import BaseModel, Field
from .auth import get_user_verified, bcrypt_context

app = APIRouter(
    prefix='/users',
    tags=['users']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_user_verified)]

class NewPasswordRequest(BaseModel):
    password: str

@app.get("/", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    return db.query(models.Users).filter(models.Users.id == user.get('id')).first()

@app.post("/change_password", status_code=status.HTTP_202_ACCEPTED)
async def change_password(user: user_dependency, db: db_dependency, new_pass_req: NewPasswordRequest):
    user = db.query(models.Users).filter(models.Users.id == user.get('id')).first()
    user.hashed_password = bcrypt_context.hash(new_pass_req.password)
    db.add(user)
    db.commit()