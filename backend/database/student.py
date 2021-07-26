from backend.database import DataBase, Table, Row


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

    @staticmethod
    def sort_by_class(student):
        return str(student.class_n) + student.class_l


class StudentsTable:
    table = "student"

    @staticmethod
    def create_table() -> None:
        DataBase.execute('''CREATE TABLE "''' + StudentsTable.table + '''
        "id"	INTEGER NOT NULL UNIQUE,
        "name_1"	TEXT NOT NULL,
        "name_2"	TEXT NOT NULL,
        "class_n"	INTEGER NOT NULL,
        "class_l"	TEXT NOT NULL,
        PRIMARY KEY("id" AUTOINCREMENT)
        );''')

    @staticmethod
    def select_all():
        return Table.select_all(StudentsTable.table, Student)

    @staticmethod
    def select_by_class_n(class_n: int) -> list:
        return Table.select_list_by_field(StudentsTable.table, 'class_n', class_n, Student)

    @staticmethod
    def select_by_student(student: Student) -> Student:
        return Table.select_by_fields(StudentsTable.table, Student, 'name_1', student.name_1, 'name_2', student.name_2,
                                           'class_n', student.class_n, 'class_l', student.class_l)

    @staticmethod
    def insert(student: Student) -> None:
        return Table.insert(StudentsTable.table, student, student.fields)

    @staticmethod
    def update(new: Student) -> None:
        return Table.update_by_field(StudentsTable.table, 'id', new)

    @staticmethod
    def delete(student: Student) -> None:
        return Table.delete(StudentsTable.table, student)
