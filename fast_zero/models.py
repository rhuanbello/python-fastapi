from datetime import datetime
from enum import Enum  # To work with date and time

from sqlalchemy import ForeignKey, func  # To use database functions like `now()`
from sqlalchemy.orm import Mapped, mapped_column, registry  # For table mapping and type hints

# Create a registry to connect classes to tables
table_registry = registry()


class TodoState(str, Enum):
    draft = 'draft'
    todo = 'todo'
    doing = 'doing'
    done = 'done'
    trash = 'trash'


# Map this class to the database as a dataclass
@table_registry.mapped_as_dataclass
class User:
    __tablename__ = 'users'  # Table name

    id: Mapped[int] = mapped_column(init=False, primary_key=True)  # Unique ID for each user (primary key & the value must not be informed)
    username: Mapped[str] = mapped_column(unique=True)  # Username (must be unique)
    password: Mapped[str]  # Password
    email: Mapped[str] = mapped_column(unique=True)  # Email (must be unique)
    created_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now())  # When the user was created (autogenerated)
    updated_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now(), onupdate=func.now())  # When the user was last updated


@table_registry.mapped_as_dataclass
class Todo:
    __tablename__ = 'todos'  # Table name

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    title: Mapped[str]  # Title
    description: Mapped[str]  # Description
    state: Mapped[TodoState]  # State (draft, todo, doing, done, trash)

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))  # User ID from the users table
