from backend.database.database import *


class Constant(Row):
    """
        Строка таблицы ConstantsTable
        name    TEXT    NOT NULL    PK  AI
        value   TEXT    NOT NULL    PK  AI
    """
    fields = ['name', 'value']

    def __init__(self, row):
        Row.__init__(self, Constant, row)


class ConstantsTable:
    table = "constant"

    @staticmethod
    def create_table() -> None:
        DataBase.execute('''CREATE TABLE "''' + ConstantsTable.table + '''" (
                "name"	TEXT NOT NULL UNIQUE,
                "value"	TEXT NOT NULL,
                PRIMARY KEY("name"));''')

    @staticmethod
    def select_all() -> list:
        return Table.select_list(ConstantsTable.table, Constant)

    @staticmethod
    def select_by_name(name: str) -> Constant:
        return Table.select_one(ConstantsTable.table, Constant, 'name', name)

