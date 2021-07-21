from backend.database import DataBase, Table, Row


class Result(Row):
    """
        Строка таблицы ResultsTable
        year        INT     NOT NULL    PK
        subject     INT     NOT NULL    PK
        user        INT     NOT NULL    PK
        result      INT     NOT NULL
        net_score   INT     NOT NULL
    """
    fields = ['year', 'subject', 'user', 'result', 'net_score']

    def __init__(self, row):
        Row.__init__(self, Result, row)

    @staticmethod
    def sort_by_result(result):
        return -result.result


class ResultsTable:
    table = "result"

    @staticmethod
    def create_table() -> None:
        DataBase.execute('''CREATE TABLE "''' + ResultsTable.table + '''" (
        "year"	INTEGER NOT NULL,
        "subject"	INTEGER NOT NULL,
        "user"	INTEGER NOT NULL,
        "result"	INTEGER NOT NULL,
        "net_score"	INTEGER NOT NULL,
        PRIMARY KEY("year","subject","user")
        );''')

    @staticmethod
    def select_all():
        return Table.select_all(ResultsTable.table, Result)

    @staticmethod
    def select_by_year(year: int) -> list:
        return Table.select_list_by_field(ResultsTable.table, 'year', year, Result)

    @staticmethod
    def select_by_year_and_subject(year: int, subject: int) -> list:
        return Table.select_list_by_fields(ResultsTable.table, Result, 'year', year, 'subject', subject)

    @staticmethod
    def select_for_people(result: Result) -> Result:
        return Table.select_by_fields(ResultsTable.table, Result, 'year', result.year, 'subject', result.subject,
                                      'user', result.user)

    @staticmethod
    def update(result: Result):
        return Table.update_by_fields(ResultsTable.table, result, 'year', result.year, 'subject', result.subject,
                                      'user', result.user)

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
