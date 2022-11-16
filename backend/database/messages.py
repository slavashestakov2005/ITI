from .database import Row, Table, Query
from datetime import datetime


class Message(Row):
    """
        Строка таблицы MessagesTable
        year        INT     NOT NULL
        title       INT     NOT NULL
        content     INT     NOT NULL
        time        TEXT    NOT NULL
    """
    fields = ['id', 'year', 'title', 'content', 'time']

    def __init__(self, row):
        Row.__init__(self, Message, row)

    def time_str(self):
        return datetime.fromtimestamp(self.time).strftime('%Y-%m-%d %H:%M:%S')


class MessagesTable(Table):
    table = "messages"
    row = Message
    create = '''(
        id          INT     NOT NULL UNIQUE KEY AUTO_INCREMENT,
        year        INT     NOT NULL,
        title	    TEXT    NOT NULL,
        content	    TEXT    NOT NULL,
        time    	INT     NOT NULL
        PRIMARY KEY(id)
        );'''

    @staticmethod
    def select_by_year(year: int) -> list:
        return Query.select_list(MessagesTable.table, Message, 'year', year)

    @staticmethod
    def select_by_year_and_title(year, title):
        return Query.select_list(MessagesTable.table, Message, 'year', year, 'title', title)

    @staticmethod
    def delete_by_year(year: int):
        return Query.delete(MessagesTable.table, 'year', year)
