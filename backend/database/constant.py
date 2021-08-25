from backend.database import Table, Row


class Constant(Row):
    """
        Строка таблицы ConstantsTable
        name    TEXT    NOT NULL    PK  UNIQUE
        value   TEXT    NOT NULL    PK
    """
    fields = ['name', 'value']

    def __init__(self, row):
        Row.__init__(self, Constant, row)


class ConstantsTable:
    table = "constant"

    @staticmethod
    def create_table() -> None:
        Table.drop_and_create(ConstantsTable.table, '''(
        "name"	TEXT NOT NULL UNIQUE,
        "value"	TEXT NOT NULL,
        PRIMARY KEY("name")
        );''')

    @staticmethod
    def select_all() -> list:
        return Table.select_list(ConstantsTable.table, Constant)

    @staticmethod
    def select_by_name(name: str) -> Constant:
        return Table.select_one(ConstantsTable.table, Constant, 'name', name)

