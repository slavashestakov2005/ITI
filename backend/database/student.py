from backend.database import Table, Row


class Student(Row):
    """
        Строка таблицы StudentsTable
        id          INT     NOT NULL    PK  AI  UNIQUE
        name_1      TEXT    NOT NULL                        (Фамилия)
        name_2      TEXT    NOT NULL                        (Имя)
        class_n     INT     NOT NULL
        class_l     TEXT    NOT NULL
    """
    fields = ['id', 'name_1', 'name_2', 'class_n', 'class_l']

    def __init__(self, row):
        Row.__init__(self, Student, row)
        self.result = 0

    def class_name(self):
        return str(self.class_n) + self.class_l

    @staticmethod
    def sort_by_class(student):
        return student.class_name()


class StudentsTable:
    table = "student"

    @staticmethod
    def create_table() -> None:
        Table.drop_and_create(StudentsTable.table, '''(
        "id"        SERIAL NOT NULL UNIQUE,
        "name_1"	TEXT NOT NULL,
        "name_2"	TEXT NOT NULL,
        "class_n"	INTEGER NOT NULL,
        "class_l"	TEXT NOT NULL,
        PRIMARY KEY("id")
        )''')

    @staticmethod
    def select_all() -> list:
        return Table.select_list_with_where(StudentsTable.table, Student, 'class_n', 4, 10)

    @staticmethod
    def select(id: int) -> Student:
        return Table.select_one(StudentsTable.table, Student, 'id', id)

    @staticmethod
    def select_by_class_n(class_n: int) -> list:
        return Table.select_list(StudentsTable.table, Student, 'class_n', class_n)

    @staticmethod
    def select_by_student(student: Student) -> Student:
        return Table.select_one(StudentsTable.table, Student, 'name_1', student.name_1, 'name_2', student.name_2,
                                'class_n', student.class_n, 'class_l', student.class_l)

    @staticmethod
    def insert(student: Student) -> None:
        return Table.insert(StudentsTable.table, student)

    @staticmethod
    def update(new: Student) -> None:
        return Table.update(StudentsTable.table, new)

    @staticmethod
    def add_class() -> None:
        return Table.update_col(StudentsTable.table, 'class_n', '1')

    @staticmethod
    def delete(student: Student) -> None:
        return Table.delete(StudentsTable.table, student)
