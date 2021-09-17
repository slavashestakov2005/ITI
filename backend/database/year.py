from backend.database import Table, Row


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


class YearsTable:
    table = "year"

    @staticmethod
    def create_table() -> None:
        Table.drop_and_create(YearsTable.table, '''(
        "year"	INTEGER NOT NULL UNIQUE,
        "message"	TEXT NOT NULL,
        "block"	INTEGER NOT NULL,
        PRIMARY KEY("year")
        )''')
        YearsTable.insert(Year([2019, '', 1]))
        YearsTable.insert(Year([2020, '', 1]))

    @staticmethod
    def select_all() -> list:
        return Table.select_list(YearsTable.table, Year)

    @staticmethod
    def select_by_year(year: int) -> Year:
        return Table.select_one(YearsTable.table, Year, 'year', year)

    @staticmethod
    def insert(year: Year) -> None:
        return Table.insert(YearsTable.table, year)

    @staticmethod
    def update(year: Year) -> None:
        return Table.update(YearsTable.table, year, 'year')

    @staticmethod
    def delete(year: int) -> None:
        return Table.delete(YearsTable.table, 'year', year)
