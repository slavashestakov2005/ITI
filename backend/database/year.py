from backend.database import Row, Table, Query


class Year(Row):
    """
        Строка таблицы YearsTable
        year    INT     NOT NULL    PK      UNIQUE
        message TEXT    NOT NULL
        block   INT     NOT NULL    (0 = 'free', 1 = 'block')
    """
    fields = ['year', 'message', 'block']

    def __init__(self, row):
        Row.__init__(self, Year, row)


class YearsTable(Table):
    table = "year"
    row = Year
    id_field = 'year'
    create = '''(
        year	INT NOT NULL UNIQUE,
        message	TEXT NOT NULL,
        block	INT NOT NULL,
        PRIMARY KEY(year)
        )'''

    @staticmethod
    def create_table() -> None:
        super().create_table()
        YearsTable.insert(Year([2019, '', 1]))
        YearsTable.insert(Year([2020, '', 1]))

    @staticmethod
    def delete(year: int) -> None:
        return Query.delete(YearsTable.table, 'year', year)
