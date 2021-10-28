from backend.database import Table, Row
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


class HistoriesTable:
    table = "history"

    @staticmethod
    def create_table() -> None:
        Table.drop_and_create(HistoriesTable.table, '''(
        id      INT NOT NULL UNIQUE KEY AUTO_INCREMENT,
        year	INT NOT NULL,
        time	INT NOT NULL,
        user	INT NOT NULL,
        type	INT NOT NULL,
        description	TEXT NOT NULL,
        revert	INT NOT NULL,
        PRIMARY KEY(id)
        )''')

    @staticmethod
    def select_all() -> list:
        return Table.select_list(HistoriesTable.table, History)

    @staticmethod
    def select(id: int) -> History:
        return Table.select_one(HistoriesTable.table, History, 'id', id)

    @staticmethod
    def insert(history: History) -> None:
        return Table.insert(HistoriesTable.table, history)

    @staticmethod
    def revert(history: History) -> None:
        return Table.update(HistoriesTable.table, history)

    @staticmethod
    def delete_by_year(year: int) -> None:
        return Table.delete(HistoriesTable.table, 'year', year)
