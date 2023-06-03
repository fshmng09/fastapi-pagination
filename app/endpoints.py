from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page, Params
from sqlalchemy.orm import Session, joinedload
import schema, models, deps
from database import engine
from fastapi_pagination.ext.sqlalchemy import paginate

api_router = APIRouter()

models.Base.metadata.create_all(bind=engine)

@api_router.post("/users", response_model=schema.User)
def create_user(user: schema.UserCreate, db: Session = Depends(deps.get_db)):
    db_user = models.User(name=user.name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@api_router.get("/users/{user_id}", response_model=schema.User)
def get_user(user_id: int, db: Session = Depends(deps.get_db)):
    print("without joined")
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    for todo in db_user.todos:
        print(todo.title)
    return db_user

@api_router.get("/joined/users/{user_id}", response_model=schema.User)
def get_user(user_id: int, db: Session = Depends(deps.get_db)):
    print("joined")
    db_user = db.query(models.User).filter(models.User.id == user_id).options(
        joinedload(models.User.todos)
    ).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    for todo in db_user.todos:
        print(todo.title)
    return db_user


def print_for_check_query(users: List[models.User]):
    for user in users:
        print(user.name)
        for todo in user.todos:
            print(todo.title)



@api_router.get("/users", response_model=List[schema.User])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(deps.get_db)):
    users = db.query(models.User).offset(skip).limit(limit).all()
    print_for_check_query(users)
    return users

@api_router.get("/joined-users", response_model=List[schema.User])
def get_joined_users(skip: int = 0, limit: int = 100, db: Session = Depends(deps.get_db)):
    users = db.query(models.User).options(
        joinedload(models.User.todos)
    ).offset(skip).limit(limit).all()
    print_for_check_query(users)
    return users

@api_router.get("/paged-joined-user", response_model=Page[schema.User])
def get_paged_joined_users(db: Session = Depends(deps.get_db), params: Params = Depends()) -> Page[schema.User]:
    paged_users = paginate(db.query(models.User).options(
        joinedload(models.User.todos)
    ), params)
    print_for_check_query(paged_users.items)
    return paged_users


# @api_router.post("/todos", response_model=schema.Todo)
# def create_todo(todo: schema.TodoCreate, db: Session = Depends(deps.get_db)):
#     db_todo = models.Todo(title=todo.title, status=todo.status)
#     db.add(db_todo)
#     db.commit()
#     db.refresh(db_todo)
#     return db_todo

# @api_router.get("/todos/{todo_id}", response_model=schema.Todo)
# def get_todo(todo_id: int, db: Session = Depends(deps.get_db)):
#     db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
#     if db_todo is None:
#         raise HTTPException(status_code=404, detail="Todo not found")
#     return db_todo

# @api_router.get("/todos", response_model=List[schema.Todo])
# def get_todos(skip: int = 0, limit: int = 100, db: Session = Depends(deps.get_db)):
#     todos = db.query(models.Todo).offset(skip).limit(limit).all()
#     return todos
