from test.test_main import client
from main import app
from fastapi import status
from router.auth import get_current_user
from database import SessionLocal
from models import Todo


app.dependency_overrides[get_current_user] = lambda: {"id": 1, "username": "testuser"}

def test_todo():
    db = SessionLocal()

    #remove old test todo if exists
    db.query(Todo).filter(Todo.id == 99).delete()

    todo = Todo(
        id=99,
        title="Test Todo", 
        description="This is a test todo", 
        priority=1, 
        completed=False, 
        owner_id=1)
    db.add(todo)
    db.commit()


def test_read_todos():
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK

def read_specific_todo():
    response = client.get("/todo/99")
    assert response.status_code == status.HTTP_200_OK

def test_create_todo():
    db = SessionLocal()
    db.query(Todo).filter(Todo.id == 0).delete()  # Remove old test todo if exists

    todo_data = {
        "id": 0,
        "title": "New test Todo",
        "description": "This is a new test todo",
        "priority": 2,
        "completed": False,
    }
    response = client.post("/create_todo", json=todo_data)
    assert response.status_code == status.HTTP_201_CREATED

def test_update_todo():

    todo_data = {
        "id": 0,
        "title": "New test Todo",
        "description": "This is a new test todo",
        "priority": 2,
        "completed": False,
    }
    response = client.put("/edit_todo/99", json=todo_data)
    assert response.status_code == status.HTTP_200_OK

def test_delete_todo():
    response = client.delete("/delete_todo/99")
    assert response.status_code == status.HTTP_200_OK