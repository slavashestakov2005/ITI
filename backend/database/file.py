from backend.database import Table, Row


class File(Row):
    """
        Строка таблицы FilesTable
        name        TEXT     NOT NULL   PK      UNIQUE
        data        BLOB     NOT NULL
    """
    fields = ['name', 'data']

    def __init__(self, row):
        Row.__init__(self, File, row)


class FilesTable:
    table = "file"

    @staticmethod
    def create_table() -> None:
        Table.drop_and_create(FilesTable.table, '''(
        "name"	TEXT NOT NULL UNIQUE,
        "data"	BYTEA NOT NULL,
        PRIMARY KEY("name")
        )''')

    @staticmethod
    def select_all() -> list:
        return Table.select_list(FilesTable.table, File)

    @staticmethod
    def select(filename: str) -> File:
        return Table.select_one(FilesTable.table, File, 'name', filename)

    @staticmethod
    def insert(file: File) -> None:
        return Table.insert(FilesTable.table, file)

    @staticmethod
    def update(file: File) -> None:
        return Table.update(FilesTable.table, file, 'name')

    @staticmethod
    def delete(filename: str) -> None:
        return Table.delete(FilesTable.table, 'name', filename)
