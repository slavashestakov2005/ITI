from .database import Row, Table, Query


class Result(Row):
    """
        Строка таблицы ResultsTable
        year        INT     NOT NULL    PK
        subject     INT     NOT NULL    PK
        user        INT     NOT NULL    PK
        result      REAL    NOT NULL
        net_score   REAL    NOT NULL
        text_result TEXT    NOT NULL
        position    INT     NOT NULL
    """
    fields = ['year', 'subject', 'user', 'result', 'net_score', 'text_result', 'position']

    def __init__(self, row):
        Row.__init__(self, Result, row)

    @staticmethod
    def sort_by_result(result):
        return -result.result


class ResultsTable(Table):
    table = "result"
    row = Result
    create = '''(
        year	    INT NOT NULL,
        subject	    INT NOT NULL,
        user	    INT NOT NULL,
        result	    REAL NOT NULL,
        net_score	REAL NOT NULL,
        text_result	TEXT NOT NULL,
        position	INT NOT NULL,
        PRIMARY KEY(year,subject,user)
        );'''

    @staticmethod
    def select_by_year(year: int) -> list:
        return Query.select_list(ResultsTable.table, Result, 'year', year)

    @staticmethod
    def select_by_year_and_subject(year: int, subject: int) -> list:
        return Query.select_list(ResultsTable.table, Result, 'year', year, 'subject', subject)

    @staticmethod
    def select_for_people(result: Result) -> Result:
        return Query.select_one(ResultsTable.table, Result, 'year', result.year, 'subject', result.subject,
                                'user', result.user)

    @staticmethod
    def update(result: Result) -> None:
        return Query.update(ResultsTable.table, result, 'year', 'subject', 'user')

    @staticmethod
    def replace(results: list) -> None:
        i = 0
        while i < len(results):
            j = min(i + 125, len(results))
            Query.replace(ResultsTable.table, results[i:j])
            i = j

    @staticmethod
    def delete_by_year(year: int) -> None:
        return Query.delete(ResultsTable.table, 'year', year)

    @staticmethod
    def delete_by_people(result: Result) -> None:
        return Query.delete(ResultsTable.table, 'year', result.year, 'subject', result.subject, 'user', result.user)
