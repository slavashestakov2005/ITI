from .database import Row, Table, Query
from datetime import datetime


class History(Row):
    """
        Строка таблицы HistoriesTable
        id          INT     NOT NULL    PK  AI  UNIQUE
        year        INT     NOT NULL
        time        INT     NOT NULL
        user        INT     NOT NULL
        type	    INT     NOT NULL
        description TEXT    NOT NULL
        revert      INT     NOT NULL
    """
    fields = ['id', 'year', 'time', 'user', 'type', 'description', 'revert']

    def __init__(self, row):
        Row.__init__(self, History, row)

    def time_str(self):
        return datetime.fromtimestamp(self.time).strftime('%Y-%m-%d %H:%M:%S')

    def rev(self):
        self.revert = True
        HistoriesTable.revert(self)


class HistoriesTable(Table):
    table = "history"
    row = History
    create = '''(
        id      INT NOT NULL UNIQUE KEY AUTO_INCREMENT,
        year	INT NOT NULL,
        time	INT NOT NULL,
        user	INT NOT NULL,
        type	INT NOT NULL,
        description	TEXT NOT NULL,
        revert	INT NOT NULL,
        PRIMARY KEY(id)
        );'''

    @staticmethod
    def select_by_year(year: int) -> list:
        return Query.select_list(HistoriesTable.table, History, 'year', year)

    @staticmethod
    def revert(history: History) -> None:
        return Query.update(HistoriesTable.table, history)

    @staticmethod
    def delete_by_year(year: int) -> None:
        return Query.delete(HistoriesTable.table, 'year', year)
