from backend.database import DataBase, Table, Row


class Result(Row):
    """
        Строка таблицы ResultsTable
        year        INT     NOT NULL    PK
        subject     INT     NOT NULL    PK
        user        INT     NOT NULL    PK
        result      INT     NOT NULL
    """
    fields = ['year', 'subject', 'user', 'result']

    def __init__(self, row):
        Row.__init__(self, Result, row)


class ResultsTable:
    table = "result"

    @staticmethod
    def create_table() -> None:
        DataBase.execute('''CREATE TABLE "''' + ResultsTable.table + '''" (
        "year"	INTEGER NOT NULL,
        "subject"	INTEGER NOT NULL,
        "user"	INTEGER NOT NULL,
        "result"	INTEGER NOT NULL,
        PRIMARY KEY("year","subject","user")
        );''')

    @staticmethod
    def select_all():
        return Table.select_all(ResultsTable.table, Result)

    @staticmethod
    def select_by_year_and_subject(year: int, subject: int) -> list:
        return Table.select_list_by_two_fields(ResultsTable.table, 'year', year, 'subject', subject, Result)

    @staticmethod
    def insert(result: Result) -> None:
        return Table.insert(ResultsTable.table, result, result.fields)
    '''
    @staticmethod
    def update_by_id(subject: Subject) -> None:
        return Table.update_by_field(SubjectsTable.table, 'id', subject)

    @staticmethod
    def delete(subject: Subject) -> None:
        return Table.delete(SubjectsTable.table, subject)
    '''
