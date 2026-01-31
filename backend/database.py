"""Работа с БД."""

import config
from sqlmodel import SQLModel, create_engine

engine = create_engine(config.DB_URL)

SQLModel.metadata.create_all(engine)
