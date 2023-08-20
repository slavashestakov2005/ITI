from datetime import datetime
from .__db_session import sa, SqlAlchemyBase, Table


class Message(SqlAlchemyBase, Table):
    __tablename__ = 'message'
    fields = ['id', 'iti_id', 'title', 'content', 'time', 'priority']

    id = sa.Column(sa.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    iti_id = sa.Column(sa.Integer, nullable=False)
    title = sa.Column(sa.String, nullable=False)
    content = sa.Column(sa.String, nullable=False)
    time = sa.Column(sa.Integer, nullable=False)
    priority = sa.Column(sa.Integer, nullable=False)

    def time_str(self, show=False):
        if not show and self.priority:
            return ''
        return datetime.fromtimestamp(self.time + 25200).strftime('%Y-%m-%d %H:%M')

    @staticmethod
    def sort_by_time(message):
        return message.priority, message.time

    # Table

    @classmethod
    def select_by_iti(cls, iti_id: int) -> list:
        return cls.__select_by_expr__(cls.iti_id == iti_id)

    @classmethod
    def select_by_iti_and_title(cls, iti_id: int, title: str) -> list:
        return cls.__select_by_expr__(cls.iti_id == iti_id, cls.title == title)

    @classmethod
    def delete_by_iti(cls, iti_id: int):
        return cls.__delete_by_expr__(cls.iti_id == iti_id)
