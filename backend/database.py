"""Работа с БД."""

from config import Config
from sqlmodel import SQLModel, create_engine

engine = create_engine(Config.db_url)

SQLModel.metadata.create_all(engine)
