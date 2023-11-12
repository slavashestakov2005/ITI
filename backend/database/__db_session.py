import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec
from .__config_db import ConfigDB
from ..help.errors import EmptyFieldException


SqlAlchemyBase = dec.declarative_base()
__factory = None


def global_init(db_file: str):
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")

    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
    print(f"Подключение к базе данных по адресу {conn_str}")

    engine = sa.create_engine(conn_str, echo="debug")
    __factory = orm.sessionmaker(bind=engine)

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()


def execute_sql(text: str, ret=False):
    if ret:
        return list(create_session().execute(sa.text(text)))
    session = create_session()
    session.execute(sa.text(text))
    session.commit()
    return None


def convert_to_dict(data):
    return {item.id: item for item in data}


class Table:
    id_field, fields = 'id', []

    def json(self):
        cls = self.__class__
        data = {}
        for field in cls.fields:
            data[field] = getattr(self, field)
        return data

    def __xor__(self, other):
        row = []
        cls = self.__class__
        for field in cls.fields:
            v1 = getattr(self, field)
            v2 = getattr(other, field)
            if v2 != '' and v2 is not None:
                row.append(v2)
            else:
                row.append(v1)
        return cls.build(*row, allow_empty=True)

    @classmethod
    def build(cls, *row, allow_empty=False):
        if len(row) == 0:
            return None
        position = 0
        fields = {}
        for field in cls.fields:
            value = row[position]
            if value == '' and not allow_empty:
                raise EmptyFieldException(field)
            fields[field] = value
            position += 1
        return cls(**fields)

    @classmethod
    def select_all(cls):
        return cls.__select_by_expr__()

    @classmethod
    def select_id_dict(cls):
        return convert_to_dict(cls.select_all())

    @classmethod
    def select_last(cls):
        session = create_session()
        values = session.query(cls).order_by(cls.id.desc()).first()
        session.expunge_all()
        session.commit()
        return values

    @classmethod
    def one_or_many(cls, data, one=False):
        return data.one_or_none() if one else data.all()

    @classmethod
    def __select_by_expr__(cls, *exprs, one=False):
        session = create_session()
        values = session.query(cls).filter(sa.and_(*exprs))
        values = cls.one_or_many(values, one)
        session.expunge_all()
        session.commit()
        return values

    @classmethod
    def select(cls, _id):
        return cls.__select_by_expr__(getattr(cls, cls.id_field) == _id, one=True)

    @classmethod
    def insert(cls, row, return_id=False):
        session = create_session()
        session.add(row)
        if return_id:
            session.flush()
            value = getattr(row, cls.id_field)
            session.commit()
            return value
        session.commit()

    @classmethod
    def __update_by_expr__(cls, row, *exprs):
        session = create_session()
        table_row = session.query(cls).filter(sa.and_(*exprs)).first()
        for field in cls.fields:
            setattr(table_row, field, getattr(row, field))
        session.commit()

    @classmethod
    def update(cls, row) -> None:
        cls.__update_by_expr__(row, getattr(cls, cls.id_field) == getattr(row, cls.id_field))

    @classmethod
    def __delete_by_expr__(cls, *exprs):
        expr = cls.__table__.delete().where(sa.and_(*exprs))
        session = create_session()
        session.execute(expr)
        session.commit()

    @classmethod
    def delete(cls, row):
        attr = row
        if issubclass(type(row), Table):
            attr = getattr(row, cls.id_field)
        cls.__delete_by_expr__(getattr(cls, cls.id_field) == attr)


from .__all_models import *
global_init(ConfigDB.DB)
