from backend.database import DataBase, Table, Row


class Student(Row):
    """
        Строка таблицы StudentsTable
        name_1      TEXT    NOT NULL    PK
        name_2      TEXT    NOT NULL    PK
        class_n     INT     NOT NULL    PK
        class_l     TEXT    NOT NULL    PK
        code        INT     NOT NULL            UNIQUE
    """
    fields = ['name_1', 'name_2', 'class_n', 'class_l', 'code']

    def __init__(self, row):
        Row.__init__(self, Student, row)


class StudentsTable:
    table = "student"

    @staticmethod
    def create_table() -> None:
        DataBase.execute('''CREATE TABLE "''' + StudentsTable.table + '''
        "name_1"	TEXT NOT NULL,
        "name_2"	TEXT NOT NULL,
        "class_n"	INTEGER NOT NULL,
        "class_l"	TEXT NOT NULL,
        "code"	INTEGER NOT NULL UNIQUE,
        PRIMARY KEY("name_1","name_2","class_n","class_l")
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
    def update_by_student(old: Student, new: Student) -> None:
        return Table.update_by_fields(StudentsTable.table, new, 'name_1', old.name_1, 'name_2', old.name_2,
                                      'class_n', old.class_n, 'class_l', old.class_l)

    @staticmethod
    def delete(student: Student) -> None:
        return Table.delete_by_fields(StudentsTable.table, 'name_1', student.name_1, 'name_2', student.name_2,
                                      'class_n', student.class_n, 'class_l', student.class_l)

