from backend.database import DataBase, Table, Row


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
    """
    fields = ['year', 'subject', 'score_5', 'score_6', 'score_7', 'score_8', 'score_9']

    def __init__(self, row):
        Row.__init__(self, YearSubject, row)


class YearsSubjectsTable:
    table = "years_subjects"

    @staticmethod
    def create_table() -> None:
        DataBase.execute('''CREATE TABLE "''' + YearsSubjectsTable.table + '''" (
        "year"	INTEGER NOT NULL,
        "subject"	INTEGER NOT NULL,
        "score_5"	INTEGER NOT NULL,
        "score_6"	INTEGER NOT NULL,
        "score_7"	INTEGER NOT NULL,
        "score_8"	INTEGER NOT NULL,
        "score_9"	INTEGER NOT NULL,
        PRIMARY KEY("year","subject")
        );''')

    @staticmethod
    def select_all():
        return Table.select_all(YearsSubjectsTable.table, YearSubject)

    @staticmethod
    def select_by_year(year: int) -> list:
        return Table.select_list_by_field(YearsSubjectsTable.table, 'year', year, YearSubject)

    @staticmethod
    def select(year: int, subject: int) -> YearSubject:
        return Table.select_by_fields(YearsSubjectsTable.table, YearSubject, 'year', year, 'subject', subject)

    @staticmethod
    def insert(year_subject: YearSubject) -> None:
        return Table.insert(YearsSubjectsTable.table, year_subject, year_subject.fields)

    @staticmethod
    def update(year_subject: YearSubject) -> None:
        return Table.update_by_fields(YearsSubjectsTable.table, year_subject,
                                      'year', year_subject.year, 'subject', year_subject.subject)

    @staticmethod
    def delete_by_year(year: int) -> None:
        return Table.delete_by_field(YearsSubjectsTable.table, 'year', year)
