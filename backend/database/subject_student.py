from backend.database import Row, Table, Query


class SubjectStudent(Row):
    """
        Строка таблицы SubjectsStudentsTable
        year        INT     NOT NULL    PK
        subject     INT     NOT NULL    PK
        student     INT     NOT NULL    PK
    """
    fields = ['year', 'subject', 'student']

    def __init__(self, row):
        Row.__init__(self, SubjectStudent, row)


class SubjectsStudentsTable(Table):
    table = "subjects_students"
    row = SubjectStudent
    create = '''(
        year	INT NOT NULL,
        subject	INT NOT NULL,
        student	INT NOT NULL,
        PRIMARY KEY(year,subject,student)
        );'''

    @staticmethod
    def select_by_year(year: int) -> list:
        return Query.select_list(SubjectsStudentsTable.table, SubjectStudent, 'year', year)

    @staticmethod
    def select_by_student(year: int, student: int) -> list:
        return Query.select_list(SubjectsStudentsTable.table, SubjectStudent, 'year', year, 'student', student)

    @staticmethod
    def select_by_subject(year: int, subject: int) -> list:
        return Query.select_list(SubjectsStudentsTable.table, SubjectStudent, 'year', year, 'subject', subject)

    @staticmethod
    def delete(subject_student: SubjectStudent) -> None:
        return Query.delete(SubjectsStudentsTable.table, 'year', subject_student.year, 'subject',
                            subject_student.subject, 'student', subject_student.student)

    @staticmethod
    def delete_by_year(year: int) -> None:
        return Query.delete(SubjectsStudentsTable.table, 'year', year)
