from backend.database import DataBase, Table, Row


class Subject(Row):
    """
        Строка таблицы SubjectsTable
        id      INT     NOT NULL    PK  AI  UNIQUE
        name    TEXT    NOT NULL            UNIQUE
    """
    fields = ['id', 'name']

    def __init__(self, row):
        Row.__init__(self, Subject, row)


class SubjectsTable:
    table = "subject"

    @staticmethod
    def create_table() -> None:
        DataBase.execute('''CREATE TABLE "''' + SubjectsTable.table + '''" (
        "id"	INTEGER NOT NULL UNIQUE,
        "name"	TEXT NOT NULL UNIQUE,
        PRIMARY KEY("id" AUTOINCREMENT)
        );''')

    @staticmethod
    def select_all():
        return Table.select_all(SubjectsTable.table, Subject)

    @staticmethod
    def select_by_name(name: str) -> Subject:
        return Table.select_by_field(SubjectsTable.table, 'name', name, Subject)

    @staticmethod
    def select_by_id(id: int) -> Subject:
        return Table.select_by_field(SubjectsTable.table, 'id', id, Subject)

    @staticmethod
    def insert(subject: Subject) -> None:
        return Table.insert(SubjectsTable.table, subject, subject.fields[1:])

    @staticmethod
    def update_by_id(subject: Subject) -> None:
        return Table.update_by_field(SubjectsTable.table, 'id', subject)

    @staticmethod
    def delete(subject: Subject) -> None:
        return Table.delete(SubjectsTable.table, subject)
