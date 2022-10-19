from .database import Row, Table, Query


class File(Row):
    """
        Строка таблицы FilesTable
        name        TEXT     NOT NULL   PK      UNIQUE
        data        BLOB     NOT NULL
    """
    fields = ['name', 'data']

    def __init__(self, row):
        Row.__init__(self, File, row)


class FilesTable(Table):
    table = "file"
    row = File
    id_field = 'name'
    create = '''(
        name    VARCHAR(256) NOT NULL UNIQUE,
        data	BLOB NOT NULL,
        PRIMARY KEY(name)
        );'''

    @staticmethod
    def delete(filename: str) -> None:
        return Query.delete(FilesTable.table, 'name', filename)
