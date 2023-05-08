import sqlalchemy as sa
from .__db_session import SqlAlchemyBase, Table, execute_sql
from .__config_db import ConfigDB


class Student(SqlAlchemyBase, Table):
    __tablename__ = 'student'
    fields = ['id', 'name_1', 'name_2', 'class_n', 'class_l', 'gender']

    id = sa.Column(sa.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    name_1 = sa.Column(sa.String, nullable=False)   # (Фамилия)
    name_2 = sa.Column(sa.String, nullable=False)   # (Имя)
    class_n = sa.Column(sa.String, nullable=False)
    class_l = sa.Column(sa.String, nullable=False)
    gender = sa.Column(sa.String, nullable=False)   # (0 - м, 1 - ж)
    result = 0

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

    # Table

    # @staticmethod
    # def select_all(year: int) -> list:
    #     if year > 0:
    #         return Query.select_list_with_where(StudentsTable.table, Student, 'class_n', 5, 9)
    #     return Query

    @classmethod
    def select_by_class_n(cls, class_n: int) -> list:
        return cls.__select_by_expr__(cls.class_n == class_n)

    @classmethod
    def select_by_student(cls, student):
        return cls.__select_by_expr__(cls.name_1==student.name_1, cls.name_2==student.name_2,
                                cls.class_n==student.class_n, cls.class_l==student.class_l, one=True)

    @classmethod
    def add_class(cls, class_n):
        sql = 'UPDATE {0} SET {1} = {1} + 1'.format(cls.__tablename__, ConfigDB.DB_COLS_PREFIX + 'class_n')
        return execute_sql(sql)
