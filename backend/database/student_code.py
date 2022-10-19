from .database import Row, Table, Query


class StudentCode(Row):
    """
        Строка таблицы StudentsCodesTable
        year        INT     NOT NULL
        code1       INT     NOT NULL
        code2       INT     NOT NULL
        student     INT     NOT NULL
    """
    fields = ['year', 'code1', 'code2', 'student']

    def __init__(self, row):
        Row.__init__(self, StudentCode, row)


class StudentsCodesTable(Table):
    table = "students_codes"
    row = StudentCode
    create = '''(
        year	INT NOT NULL,
        code1	INT NOT NULL,
        code2	INT NOT NULL,
        student	INT NOT NULL
        );'''

    @staticmethod
    def select_by_year(year: int) -> list:
        return Query.select_list(StudentsCodesTable.table, StudentCode, 'year', year)

    @staticmethod
    def select_by_code(year: int, code: int, day: int = None) -> StudentCode:
        if day == 3:
            day = 2
        if not day:
            # r1 = Query.select_one(StudentsCodesTable.table, StudentCode, 'year', year, 'code1', code)
            # r2 = Query.select_one(StudentsCodesTable.table, StudentCode, 'year', year, 'code2', code)
            # return set([r1, r2])
            return [StudentsCodesTable.select_by_code(year, code, 1)]
        return Query.select_one(StudentsCodesTable.table, StudentCode, 'year', year, 'code' + str(day), code)

    @staticmethod
    def select_by_student(year: int, student: int) -> StudentCode:
        return Query.select_one(StudentsCodesTable.table, StudentCode, 'year', year, 'student', student)

    @staticmethod
    def insert_all(codes: list) -> None:
        i = 0
        while i < len(codes):
            j = min(i + 125, len(codes))
            Query.insert(StudentsCodesTable.table, codes[i:j])
            i = j

    @staticmethod
    def delete_by_year(year: int) -> None:
        return Query.delete(StudentsCodesTable.table, 'year', year)
