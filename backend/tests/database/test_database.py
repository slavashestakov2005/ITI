import pytest
from config import Config
from models import User

Config.db_url = "sqlite:///database_test.db"

from database import engine
from sqlmodel import Session, SQLModel, select

SQLModel.metadata.drop_all(engine)
SQLModel.metadata.create_all(engine)


def test_user_get():
    test_user = User(login="test", password="ttestt", name="teeeest")

    with Session(engine) as session:
        session.add(test_user)
        session.commit()

    with Session(engine) as session:
        get_user = session.exec(select(User).where(User.login == "test")).first()

    assert get_user.id == 1


def test_user_pop():
    with Session(engine) as session:
        get_user = session.get(User, 1)
        session.delete(get_user)
        session.commit()

    with Session(engine) as session:
        get_user = session.exec(select(User).where(User.login == "test")).first()
        assert get_user == None
