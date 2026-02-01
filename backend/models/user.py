"""Модель пользователя."""

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """Модель пользователя."""

    id: int | None = Field(default=None, primary_key=True)
    login: str
    name: str
    password: str
