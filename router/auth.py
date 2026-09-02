from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from typing import Annotated, Optional
from pydantic import BaseModel, Field
from models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone


router=APIRouter()

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY ="d7efb5b2b0291236fe333151f27726ab5a67056a5858866080acdae31d0cf6b3"
ALGORITHM = "HS256"
OAuth2_bearer = OAuth2PasswordBearer(tokenUrl="login")

class CreateUsers(BaseModel):
    email: str
    username: str
    firstname: str
    lastname: str
    role: str = "user"
    password: str
    phone_number: str

class UpdateUser(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    phone_number: Optional[str] = None


class ChangePassword(BaseModel):
    current_password: str
    new_password: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

def get_current_user(db: db_dependency, token: Annotated[str, Depends(OAuth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        role: str = payload.get("role")
        if username is None or user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    return {"username": username, "id": user_id, "role": role}


user_dependency = Annotated[dict, Depends(get_current_user)]


def create_access_token(
    username: str,
    user_id: int,
    role: str,
    expires_delta: timedelta = timedelta(minutes=30),
):
    encode={"sub": username, "id": user_id, "role": role}
    expire = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expire})

    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def authenticate_user(username,password, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    
    if not bcrypt_context.verify(password, user.hash_password):
        return False
    
    return user

@router.post("/create_user")
def create_users(db: db_dependency, new_user: CreateUsers):
    
    user_model = Users()

    user_model.email = new_user.email
    user_model.username = new_user.username
    user_model.firstname = new_user.firstname
    user_model.lastname = new_user.lastname
    user_model.role = new_user.role
    user_model.hash_password = bcrypt_context.hash(new_user.password)
    user_model.phone_number = new_user.phone_number 

    db.add(user_model)
    db.commit()

    return {"message": "User created successfully"}

@router.post("/login")
def login_user(db: db_dependency, form_data:Annotated[OAuth2PasswordRequestForm, Depends()]):

    user = authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    else:
        token=create_access_token(user.username, user.id, user.role, expires_delta=timedelta(minutes=30))
        return {"access_token": token, "token_type": "bearer"}


@router.put("/edit_user")
def update_todos(db: db_dependency, update_user: UpdateUser, user: user_dependency):  
    if not user:
            raise HTTPException(status_code=401, detail="Unauthorized")

    user=db.query(Users).filter(Users.id==user["id"]).first()

    updated_user= update_user.model_dump(exclude_unset=True)
    for key, value in updated_user.items():
        setattr(user, key, value)

    db.commit()


    return {
        "status": 200,
        "transaction": "User Updated Successful"
    }

@router.put("/change_password")
def change_password(db: db_dependency, updated_password: ChangePassword ,user: user_dependency):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user = db.query(Users).filter(Users.id == user["id"]).first()

    if not bcrypt_context.verify(updated_password.current_password, user.hash_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    user.hash_password = bcrypt_context.hash(updated_password.new_password)

    db.add(user)
    db.commit()
    return {
        "status": 200,
        "transaction": "Password changed successfully"
    }