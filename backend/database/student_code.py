from backend.database import Table, Row


class StudentCode(Row):
    """
        Строка таблицы StudentsCodesTable
        year        INT     NOT NULL    PK
        code1       INT     NOT NULL
        code2       INT     NOT NULL
        student     INT     NOT NULL
    """
    fields = ['year', 'code1', 'code2', 'student']

    def __init__(self, row):
        Row.__init__(self, StudentCode, row)


class StudentsCodesTable:
    table = "students_codes"

    @staticmethod
    def create_table() -> None:
        Table.drop_and_create(StudentsCodesTable.table, '''(
        year	INT NOT NULL,
        code1	INT NOT NULL,
        code2	INT NOT NULL,
        student	INT NOT NULL,
        PRIMARY KEY(year)
        )''')

    @staticmethod
    def select_all() -> list:
        return Table.select_list(StudentsCodesTable.table, StudentCode)

    @staticmethod
    def select_by_year(year: int) -> list:
        return Table.select_list(StudentsCodesTable.table, StudentCode, 'year', year)

    @staticmethod
    def select_by_code(year: int, code: int, day: int = None) -> StudentCode:
        if not day:
            r1 = Table.select_one(StudentsCodesTable.table, StudentCode, 'year', year, 'code1', code)
            r2 = Table.select_one(StudentsCodesTable.table, StudentCode, 'year', year, 'code2', code)
            return set([r1, r2])
        return Table.select_one(StudentsCodesTable.table, StudentCode, 'year', year, 'code' + str(day), code)

    @staticmethod
    def select_by_student(year: int, student: int) -> StudentCode:
        return Table.select_one(StudentsCodesTable.table, StudentCode, 'year', year, 'student', student)

    @staticmethod
    def insert(student_code: StudentCode) -> None:
        return Table.insert(StudentsCodesTable.table, student_code)

    @staticmethod
    def insert_all(codes: list) -> None:
        i = 0
        while i < len(codes):
            j = min(i + 125, len(codes))
            Table.insert(StudentsCodesTable.table, codes[i:j])
            i = j

    @staticmethod
    def delete_by_year(year: int) -> None:
        return Table.delete(StudentsCodesTable.table, 'year', year)
