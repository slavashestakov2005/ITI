"""Модель новости."""

from sqlmodel import Field, SQLModel


class News(SQLModel, table=True):
    """Модель новости."""

    id: int | None = Field(default=None, primary_key=True)
    title: str
    text: str
    has_image: bool
