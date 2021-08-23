from backend.database import DataBase, Table, Row


class Appeal(Row):
    """
        Строка таблицы AppealsTable
        year        INT     NOT NULL
        subject     INT     NOT NULL
        student     INT     NOT NULL
        tasks       TEXT    NOT NULL
        description TEXT    NOT NULL
    """
    fields = ['year', 'subject', 'student', 'tasks', 'description']

    def __init__(self, row):
        Row.__init__(self, Appeal, row)


class AppealsTable:
    table = "appeal"

    @staticmethod
    def create_table() -> None:
        DataBase.execute('''CREATE TABLE "''' + AppealsTable.table + '''" (
        "year"	INTEGER NOT NULL,
        "subjects"	INTEGER NOT NULL,
        "student"	INTEGER NOT NULL,
        "tasks"	TEXT NOT NULL,
        "description"	TEXT NOT NULL
        );''')

    @staticmethod
    def select_all() -> list:
        return Table.select_list(AppealsTable.table, Appeal)

    @staticmethod
    def select_by_year_and_subject(year: int, subject: int) -> list:
        return Table.select_list(AppealsTable.table, Appeal, 'year', year, 'subject', subject)

    @staticmethod
    def insert(appeal: Appeal) -> None:
        return Table.insert(AppealsTable.table, appeal)
