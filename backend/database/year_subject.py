from backend.database import Row, Table, Query
from datetime import datetime


class YearSubject(Row):
    """
        Строка таблицы YearsSubjectsTable
        year        INT     NOT NULL    PK
        subject     INT     NOT NULL    PK
        score_5     INT     NOT NULL
        score_6     INT     NOT NULL
        score_7     INT     NOT NULL
        score_8     INT     NOT NULL
        score_9     INT     NOT NULL
        start       INT     NOT NULL
        end         INT     NOT NULL
        classes     TEXT    NOT NULL
        place       TEXT    NOT NULL
        n_d         INT     NOT NULL
    """
    fields = ['year', 'subject', 'score_5', 'score_6', 'score_7', 'score_8', 'score_9', 'start', 'end', 'classes',
              'place', 'n_d']

    def __init__(self, row):
        Row.__init__(self, YearSubject, row)

    @staticmethod
    def sort_by_start(year_subject):
        return year_subject.start

    def date_str(self) -> str:
        return datetime.fromtimestamp(self.start).strftime('%Y-%m-%d')

    def start_str(self) -> str:
        return datetime.fromtimestamp(self.start).strftime('%H:%M')

    def end_str(self) -> str:
        return datetime.fromtimestamp(self.end).strftime('%H:%M')


class YearsSubjectsTable(Table):
    table = "years_subjects"
    row = YearSubject
    create = '''(
        year	INT NOT NULL,
        subject	INT NOT NULL,
        score_5	INT NOT NULL,
        score_6	INT NOT NULL,
        score_7	INT NOT NULL,
        score_8	INT NOT NULL,
        score_9	INT NOT NULL,
        start	INT NOT NULL,
        end	INT NOT NULL,
        classes	TEXT NOT NULL,
        place	TEXT NOT NULL,
        n_d	INT NOT NULL,
        PRIMARY KEY(year,subject)
        );'''

    @staticmethod
    def select_by_year(year: int) -> list:
        return Query.select_list(YearsSubjectsTable.table, YearSubject, 'year', year)

    @staticmethod
    def select(year: int, subject: int) -> YearSubject:
        return Query.select_one(YearsSubjectsTable.table, YearSubject, 'year', year, 'subject', subject)

    @staticmethod
    def update(year_subject: YearSubject) -> None:
        return Query.update(YearsSubjectsTable.table, year_subject, 'year', 'subject')

    @staticmethod
    def delete_by_year(year: int) -> None:
        return Query.delete(YearsSubjectsTable.table, 'year', year)

    @staticmethod
    def delete(year: int, subject: int) -> None:
        return Query.delete(YearsSubjectsTable.table, 'year', year, 'subject', subject)
