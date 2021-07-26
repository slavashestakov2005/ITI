from backend.database.database import *


class StudentCode(Row):
    """
        Строка таблицы StudentsCodesTable
        year        INT     NOT NULL    PK
        code        INT     NOT NULL    PK
        student     INT     NOT NULL
    """
    fields = ['year', 'code', 'student']

    def __init__(self, row):
        Row.__init__(self, StudentCode, row)


class StudentsCodesTable:
    table = "students_codes"

    @staticmethod
    def create_table() -> None:
        DataBase.execute('''CREATE TABLE "''' + StudentsCodesTable.table + '''" (
        "year"	INTEGER NOT NULL,
        "code"	INTEGER NOT NULL,
        "student"	INTEGER NOT NULL,
        PRIMARY KEY("code","year")
        );''')

    @staticmethod
    def select_all():
        return Table.select_all(StudentsCodesTable.table, StudentCode)

    @staticmethod
    def select_by_year(year: int) -> list:
        return Table.select_list_by_field(StudentsCodesTable.table, 'year', year, StudentCode)

    @staticmethod
    def select_by_code(year: int, code: int) -> StudentCode:
        return Table.select_by_fields(StudentsCodesTable.table, StudentCode, 'year', year, 'code', code)

    @staticmethod
    def insert(student_code: StudentCode) -> None:
        return Table.insert_all_columns(StudentsCodesTable.table, student_code)

    @staticmethod
    def insert_all(codes: list) -> None:
        return Table.insert_rows(StudentsCodesTable.table, codes)

    @staticmethod
    def delete_by_year(year: int) -> None:
        return Table.delete_by_field(StudentsCodesTable.table, 'year', year)
