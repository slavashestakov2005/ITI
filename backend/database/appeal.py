from .database import Row, Table, Query


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


class AppealsTable(Table):
    table = "appeal"
    row = Appeal
    create = '''(
        year	    INT     NOT NULL,
        subject	    INT     NOT NULL,
        student	    INT     NOT NULL,
        tasks	    TEXT    NOT NULL,
        description	TEXT    NOT NULL
        );'''

    @staticmethod
    def select_by_year(year: int) -> list:
        return Query.select_list(AppealsTable.table, Appeal, 'year', year)

    @staticmethod
    def select_by_year_and_subject(year: int, subject: int) -> list:
        return Query.select_list(AppealsTable.table, Appeal, 'year', year, 'subject', subject)

    @staticmethod
    def delete_by_year(year: int) -> None:
        return Query.delete(AppealsTable.table, 'year', year)
