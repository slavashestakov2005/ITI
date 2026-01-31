"""Работа с БД."""

from sqlmodel import SQLModel, create_engine

engine = create_engine("sqlite:///database.db")

SQLModel.metadata.create_all(engine)
