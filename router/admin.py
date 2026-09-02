from fastapi import FastAPI, APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from typing import Annotated
from pydantic import BaseModel, Field
from models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from router.auth import get_current_user
from models import Todo

router=APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/admin/todos")
def read_users(db: db_dependency, user: user_dependency):
    if not user or user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Forbidden: You do not have access to this resource")
    
    return db.query(Todo).all()

@router.delete("/admin/delete_todo/{todo_id}")
def delete_todos(db: db_dependency, todo_id: int,user: user_dependency):
    if not user or user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Forbidden: You do not have access to this resource")
    
    todos = db.query(Todo).filter(Todo.id == todo_id).first()

    if not todos:
        raise HTTPException(status_code=404, detail="Todo not found")

    db.delete(todos)
    db.commit()

    return {
        "status": 200,
        "transaction": "Successfully deleted the todo"
    }