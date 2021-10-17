from backend.database import Table, Row


class Result(Row):
    """
        Строка таблицы ResultsTable
        year        INT     NOT NULL    PK
        subject     INT     NOT NULL    PK
        user        INT     NOT NULL    PK
        result      REAL    NOT NULL
        net_score   INT     NOT NULL
        text_result TEXT    NOT NULL
        position    INT     NOT NULL
    """
    fields = ['year', 'subject', 'user', 'result', 'net_score', 'text_result', 'position']

    def __init__(self, row):
        Row.__init__(self, Result, row)

    @staticmethod
    def sort_by_result(result):
        return -result.result


class ResultsTable:
    table = "result"

    @staticmethod
    def create_table() -> None:
        Table.drop_and_create(ResultsTable.table, '''(
        "year"	INTEGER NOT NULL,
        "subject"	INTEGER NOT NULL,
        "user"	INTEGER NOT NULL,
        "result"	REAL NOT NULL,
        "net_score"	INTEGER NOT NULL,
        "text_result"	TEXT NOT NULL,
        "position"	INTEGER NOT NULL,
        PRIMARY KEY("year","subject","user")
        )''')

    @staticmethod
    def select_all() -> list:
        return Table.select_list(ResultsTable.table, Result)

    @staticmethod
    def select_by_year(year: int) -> list:
        return Table.select_list(ResultsTable.table, Result, 'year', year)

    @staticmethod
    def select_by_year_and_subject(year: int, subject: int) -> list:
        return Table.select_list(ResultsTable.table, Result, 'year', year, 'subject', subject)

    @staticmethod
    def select_for_people(result: Result) -> Result:
        return Table.select_one(ResultsTable.table, Result, 'year', result.year, 'subject', result.subject,
                                'user', result.user)

    @staticmethod
    def update(result: Result) -> None:
        return Table.update(ResultsTable.table, result, 'year', 'subject', 'user')

    @staticmethod
    def insert(result: Result) -> None:
        return Table.insert(ResultsTable.table, result)

    @staticmethod
    def delete_by_year(year: int) -> None:
        return Table.delete(ResultsTable.table, 'year', year)

    @staticmethod
    def delete_by_people(result: Result) -> None:
        return Table.delete(ResultsTable.table, 'year', result.year, 'subject', result.subject, 'user', result.user)
