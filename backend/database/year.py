from backend.database import DataBase, Table, Row


class Year(Row):
    """
        Строка таблицы YearsTable
        year    INT     NOT NULL    PK      UNIQUE
    """
    fields = ['year']

    def __init__(self, row):
        Row.__init__(self, Year, row)


class YearsTable:
    table = "year"

    @staticmethod
    def create_table() -> None:
        DataBase.execute('''CREATE TABLE "''' + YearsTable.table + '''" (
        "year"	INTEGER NOT NULL UNIQUE,
        PRIMARY KEY("year")
        );''')

    @staticmethod
    def select_all():
        return Table.select_all(YearsTable.table, Year)

    @staticmethod
    def select_by_year(year: int) -> Year:
        return Table.select_by_field(YearsTable.table, 'year', year, Year)

    @staticmethod
    def insert(year: Year) -> None:
        return Table.insert(YearsTable.table, year, year.fields)
