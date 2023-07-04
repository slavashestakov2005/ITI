from .__db_session import sa, SqlAlchemyBase, Table, execute_sql
from .student_class import StudentClass


class Student(SqlAlchemyBase, Table):
    __tablename__ = 'student'
    fields = ['id', 'name_1', 'name_2', 'gender']

    id = sa.Column(sa.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    name_1 = sa.Column(sa.String, nullable=False)   # (Фамилия)
    name_2 = sa.Column(sa.String, nullable=False)   # (Имя)
    gender = sa.Column(sa.String, nullable=False)   # (0 - м, 1 - ж)
    result = 0

    def load_class(self, year: int):
        sc = StudentClass.select(year, self.id)
        if not sc:
            return False
        self.class_l = sc.class_latter
        self.class_n = sc.class_number
        return True

    def class_name(self):
        try:
            return str(self.class_n) + self.class_l
        except Exception:
            raise ValueError("Not found class for {}, id: {}".format(self.name(), self.id))

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

    # Table

    @classmethod
    def select_all_by_year(cls, year: int) -> list:
        students = Student.select_all()
        students = [student for student in students if student.load_class(year)]
        return students

    @classmethod
    def select_by_year(cls, year: int) -> list:
        cls1, cls2 = 2, 4
        if year > 0:
            cls1, cls2 = 5, 9
        return [student for student in Student.select_all_by_year(year) if cls1 <= student.class_n <= cls2]

    @classmethod
    def select_by_class_n(cls, year: int, class_n: int) -> list:
        return [student for student in Student.select_all_by_year(year) if student.class_n == class_n]

    @classmethod
    def select_by_name(cls, name1, name2) -> list:
        return cls.__select_by_expr__(cls.name_1 == name1, cls.name_2 == name2)
