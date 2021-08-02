from backend.database import DataBase, Table, Row


class Subject(Row):
    """
        Строка таблицы SubjectsTable
        id      INT     NOT NULL    PK  AI  UNIQUE
        name    TEXT    NOT NULL            UNIQUE
        type    TEXT    NOT NULL    ('i' / 'g' / 'a')
    """
    fields = ['id', 'name', 'type']

    def __init__(self, row):
        Row.__init__(self, Subject, row)


class SubjectsTable:
    table = "subject"

    @staticmethod
    def create_table() -> None:
        DataBase.execute('''CREATE TABLE "''' + SubjectsTable.table + '''" (
        "id"	INTEGER NOT NULL UNIQUE,
        "name"	TEXT NOT NULL UNIQUE,
        "type"	TEXT NOT NULL,
        PRIMARY KEY("id" AUTOINCREMENT)
        );''')

    @staticmethod
    def select_all() -> list:
        return Table.select_list(SubjectsTable.table, Subject)

    @staticmethod
    def select_by_name(name: str) -> Subject:
        return Table.select_one(SubjectsTable.table, Subject, 'name', name)

    @staticmethod
    def select_by_id(id: int) -> Subject:
        return Table.select_one(SubjectsTable.table, Subject, 'id', id)

    @staticmethod
    def insert(subject: Subject) -> None:
        return Table.insert(SubjectsTable.table, subject)

    @staticmethod
    def update_by_id(subject: Subject) -> None:
        return Table.update(SubjectsTable.table, subject)

    @staticmethod
    def delete(subject: Subject) -> None:
        return Table.delete(SubjectsTable.table, subject)
