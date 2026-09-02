from fastapi import FastAPI, Depends, HTTPException
import models
from database import engine, SessionLocal
from typing import Annotated,Optional
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from router import auth,admin

app = FastAPI()

models.Base.metadata.create_all(bind=engine)
app.include_router(auth.router)  #connecting auth.py with main.py
app.include_router(admin.router) #connecting admin.py with main.py

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(auth.get_current_user)]

class Todos(BaseModel):  #input validaton with pycantic
    title: str
    description: str=Field(default=None, title="The description of the todo", max_length=300)
    priority: int=Field(default=1, title="The priority of the todo", ge=0, le=6)
    completed: bool

class TodosUpdate(BaseModel):  #input validaton with pycantic
    # jehetu id ta URL-e thakbe, tai ekhane id lagbe na
    title: Optional[str] = None
    description: Optional[str] = Field(default=None, title="The description of the todo", max_length=300)
    priority: Optional[int] = Field(default=1, title="The priority of the todo", ge=0, le=6)
    completed: Optional[bool] = None

@app.get("/")
def read(db: db_dependency, user: user_dependency): 
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    todos = db.query(models.Todo).filter(models.Todo.owner_id==user["id"]).all()
    return todos

@app.get("/todo/{todo_id}")
def read_todos(db: db_dependency, todo_id: int, user: user_dependency):  
    specific_todo = db.query(models.Todo).filter(models.Todo.owner_id==user["id"]).filter(models.Todo.id == todo_id).first()
    if not specific_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    if specific_todo.owner_id != user["id"]:
        raise HTTPException(status_code=403, detail="Forbidden: You do not have access to this todo")
    else:
        return specific_todo 
    
@app.post("/create_todo")
def create_todo(db: db_dependency, todo: Todos, user: user_dependency):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    todo_model = models.Todo()
    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.priority = todo.priority
    todo_model.completed = todo.completed
    todo_model.owner_id = user.get("id")  # Set the owner_id to the current user's id

    db.add(todo_model)
    db.commit()

    return {
        "status": 201,
        "transaction": "Successful"
    }


@app.put("/edit_todo/{todo_id}")
def update_todos(db: db_dependency, todo_id: int, update_todo: TodosUpdate, user: user_dependency):  
    todos = db.query(models.Todo).filter(models.Todo.owner_id==user["id"]).filter(models.Todo.id == todo_id).first()
    if not user:
            raise HTTPException(status_code=401, detail="Unauthorized")
    if not todos:
        raise HTTPException(status_code=404, detail="Todo not found")

    update_data = update_todo.model_dump(exclude_unset=True) 
    for key, value in update_data.items():
        setattr(todos, key, value)

    db.add(todos)
    db.commit()


    return {
        "status": 200,
        "transaction": "Successful"
    }


@app.delete("/delete_todo/{todo_id}")
def delete_todos(db: db_dependency, todo_id: int,user: user_dependency):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    todos = db.query(models.Todo).filter(models.Todo.owner_id==user["id"]).filter(models.Todo.id == todo_id).first()
    if not todos:
        raise HTTPException(status_code=404, detail="Todo not found")

    db.delete(todos)
    db.commit()

    return {
        "status": 200,
        "transaction": "Successful"
    }

@app.get("/user")
def get_user(db: db_dependency, user: user_dependency):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return db.query(models.Users).filter(models.Users.id == user["id"]).first()

