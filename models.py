from database import Base
from sqlalchemy import (Column, Integer, 
                        String, Boolean,
                        ForeignKey)

class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    priority = Column(Integer, index=True)
    completed = Column(Boolean, default=False)
    owner_id = Column(Integer,ForeignKey("users.id"))  # Foreign key to the Users table  


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(200), unique=True, index=True)
    username = Column(String(45), unique=True, index=True)
    firstname = Column(String(45))
    lastname = Column(String(45)) 
    is_active = Column(Boolean, default=True)
    role = Column(String(45), default="user")
    hash_password = Column(String)
    phone_number = Column(String(15)) #eita alembic diye pore database e add kora hoise mane api diye db update kora jabe na,
                                      #sudhu alembic diye update kora jabe.