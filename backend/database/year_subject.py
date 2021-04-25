from backend.database import DataBase, Table, Row


class YearSubject(Row):
    """
        Строка таблицы YearsSubjectsTable
        year        INT     NOT NULL    PK
        subject     INT     NOT NULL    PK
    """
    fields = ['year', 'subject']

    def __init__(self, row):
        Row.__init__(self, YearSubject, row)


class YearsSubjectsTable:
    table = "years_subjects"

    @staticmethod
    def create_table() -> None:
        DataBase.execute('''CREATE TABLE "''' + YearsSubjectsTable.table + '''" (
        "year"	INTEGER NOT NULL,
        "subject"	INTEGER NOT NULL,
        PRIMARY KEY("year","subject")
        );''')

    @staticmethod
    def select_all():
        return Table.select_all(YearsSubjectsTable.table, YearSubject)

    @staticmethod
    def select_by_year(year: int) -> list:
        return Table.select_list_by_field(YearsSubjectsTable.table, 'year', year, YearSubject)

    @staticmethod
    def insert(year_subject: YearSubject) -> None:
        return Table.insert(YearsSubjectsTable.table, year_subject, year_subject.fields)

    @staticmethod
    def delete_by_year(year: int) -> None:
        return Table.delete_by_field(YearsSubjectsTable.table, 'year', year)
