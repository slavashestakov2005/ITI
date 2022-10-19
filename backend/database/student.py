from .database import Row, Table, Query


class Student(Row):
    """
        Строка таблицы StudentsTable
        id          INT     NOT NULL    PK  AI  UNIQUE
        name_1      TEXT    NOT NULL                        (Фамилия)
        name_2      TEXT    NOT NULL                        (Имя)
        class_n     INT     NOT NULL
        class_l     TEXT    NOT NULL
        gender      INT                                     (0 - м, 1 - ж)
    """
    fields = ['id', 'name_1', 'name_2', 'class_n', 'class_l', 'gender']

    def __init__(self, row):
        Row.__init__(self, Student, row)
        self.result = 0

    def class_name(self):
        return str(self.class_n) + self.class_l

    def name(self):
        return self.name_1 + ' ' + self.name_2

    def get_gender(self):
        return 'Ж' if self.gender else 'М'

    def set_gender(self, s):
        self.gender = 0
        if s == 'Ж' or s == 'ж':
            self.gender = 1

    @staticmethod
    def sort_by_class(student):
        return student.class_name()

    @staticmethod
    def sort_by_name(student):
        return student.name()


class StudentsTable(Table):
    table = "student"
    row = Student
    create = '''(
        id      INT     NOT NULL UNIQUE KEY AUTO_INCREMENT,
        name_1	TEXT    NOT NULL,
        name_2	TEXT    NOT NULL,
        class_n	INT     NOT NULL,
        class_l	TEXT NOT NULL,
        gender  INT,
        PRIMARY KEY(id)
        );'''

    @staticmethod
    def select_all(year: int) -> list:
        if year > 0:
            return Table.select_list_with_where(StudentsTable.table, Student, 'class_n', 4, 10)
        return Table.select_list_with_where(StudentsTable.table, Student, 'class_n', 1, 5)

    @staticmethod
    def select_by_class_n(class_n: int) -> list:
        return Query.select_list(StudentsTable.table, Student, 'class_n', class_n)

    @staticmethod
    def select_by_student(student: Student) -> Student:
        return Query.select_one(StudentsTable.table, Student, 'name_1', student.name_1, 'name_2', student.name_2,
                                'class_n', student.class_n, 'class_l', student.class_l)

    @staticmethod
    def add_class() -> None:
        return Query.update_col(StudentsTable.table, 'class_n', '1')

