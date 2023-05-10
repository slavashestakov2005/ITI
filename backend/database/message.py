from datetime import datetime
from .__db_session import sa, SqlAlchemyBase, Table


class Message(SqlAlchemyBase, Table):
    __tablename__ = 'messages'
    fields = ['id', 'year', 'title', 'content', 'time']

    id = sa.Column(sa.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    year = sa.Column(sa.Integer, nullable=False)
    title = sa.Column(sa.String, nullable=False)
    content = sa.Column(sa.String, nullable=False)
    time = sa.Column(sa.Integer, nullable=False)

    def year_start(self):
        return int(datetime(abs(self.year), 1, 1, 0, 0).timestamp())

    def time_str(self, show=False):
        if not show and self.time - self.year_start() < 24 * 60 * 60:
            return ''
        return datetime.fromtimestamp(self.time + 25200).strftime('%Y-%m-%d %H:%M')

    @staticmethod
    def sort_by_time(message):
        return message.time + 10 ** 8 if message.time - message.year_start() < 24 * 60 * 60 else message.time

    # Table

    @classmethod
    def select_by_year(cls, year: int) -> list:
        return cls.__select_by_expr__(cls.year == year)

    @classmethod
    def select_by_year_and_title(cls, year: int, title: str) -> list:
        return cls.__select_by_expr__(cls.year == year, cls.title == title)

    @classmethod
    def delete_by_year(cls, year: int):
        return cls.__delete_by_expr__(cls.year == year)
