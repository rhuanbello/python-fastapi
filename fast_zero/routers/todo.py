from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import Todo, TodoState, User
from fast_zero.schemas import Message, TodoList, TodoPublic, TodoSchema, TodoUpdate
from fast_zero.security import get_current_user

router = APIRouter(prefix='/todos', tags=['/todos'])
T_Session = Annotated[Session, Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=TodoPublic)
def create_todo(todo: TodoSchema, session: T_Session, current_user: T_CurrentUser):
    db_todo = Todo(  # type: ignore
        title=todo.title, description=todo.description, state=todo.state, user_id=current_user.id
    )

    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)

    return db_todo


@router.get('/', status_code=HTTPStatus.OK, response_model=TodoList)
def list_todos(
    session: T_Session,
    current_user: T_CurrentUser,
    title: str | None = None,
    description: str | None = None,
    state: TodoState | None = None,
    offset: int | None = None,
    limit: int | None = None,
):
    query = select(Todo).where(Todo.user_id == current_user.id)

    if title:
        query = query.where(Todo.title.icontains(title))

    if description:
        query = query.where(Todo.description.icontains(description))

    if state:
        query = query.where(Todo.state == state)

    if offset:
        query = query.offset(offset)

    if limit:
        query = query.limit(limit)

    todos = session.scalars(query)

    return {'todos': todos}


@router.delete('/{todo_id}', response_model=Message)
def delete_todo(todo_id: int, session: T_Session, current_user: T_CurrentUser):
    todo = session.scalar(select(Todo).where(Todo.user_id == current_user.id, Todo.id == todo_id))

    if not todo:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Todo not found')

    session.delete(todo)
    session.commit()

    return {'message': 'Todo deleted'}


@router.patch('/{todo_id}', response_model=TodoPublic)
def patch_todo(todo_id: int, session: T_Session, current_user: T_CurrentUser, todo: TodoUpdate):
    db_todo = session.scalar(select(Todo).where(Todo.user_id == current_user.id, Todo.id == todo_id))

    if not db_todo:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Todo not found')

    for key, value in todo.model_dump(exclude_unset=True).items():
        setattr(db_todo, key, value)

    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)

    return db_todo
