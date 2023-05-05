from database import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean

class Users(Base):
    __tablename__  = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    firstName = Column(String)
    lastName = Column(String)
    hashedPassword = Column(String)
    isActive = Column(Boolean, default=True)
    role = Column(String)

class Todos(Base):
    __tablename__ = 'todos'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    ownerId = Column(Integer, ForeignKey("users.id"))