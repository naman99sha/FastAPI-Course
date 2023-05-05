from datetime import datetime, timedelta
from typing import Annotated
from database import SessionLocal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from models import Users
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
import jwt

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

SECRET_KEY = '42c26682108995dcb7a0dc23523e977e213377e0c8c9ed7c7acc31fa2099f38e'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated = 'auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/login')

class UserValidation(BaseModel):
    username : str
    email : str
    firstName : str
    lastName : str
    password : str
    role : str
    
class Token(BaseModel):
    access_token: str
    token_type: str
    
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
db_dependency = Annotated[Session, Depends(get_db)]

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, createUserReq: UserValidation):
    userModel = Users(
        email = createUserReq.email,
        username = createUserReq.username,
        firstName = createUserReq.firstName,
        lastName = createUserReq.lastName,
        role = createUserReq.role,
        hashedPassword = bcrypt_context.hash(createUserReq.password),
        isActive = True
    )
    db.add(userModel)
    db.commit()

def authenticateUser(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashedPassword):
        return False
    return user

def createJwt(username: str, userId: int, role: str, expires: timedelta):
    encode = {
        'sub': username, 
        'id' : userId,
        'role': role,
        'exp': datetime.utcnow() + expires
    }
    return jwt.encode(encode, SECRET_KEY, algorithm = ALGORITHM)

async def get_user_verified(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get('sub')
        userId = payload.get('id')
        role = payload.get('role')
        if username is None or userId is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate")
        return {'username':username, 'id':userId, 'role':role}
    except jwt.exceptions.InvalidSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate")
    
@router.post("/login", status_code=status.HTTP_202_ACCEPTED, response_model=Token)
async def login_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticateUser(form_data.username, form_data.password, db)
    if user:
        token = createJwt(user.username, user.id, user.role, timedelta(minutes=20))
        return {"access_token":token, "token_type":"Bearer"}
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate")

@router.get("/users", status_code= status.HTTP_200_OK)
async def return_users(db: db_dependency):
    usersList = db.query(Users).all()
    return usersList