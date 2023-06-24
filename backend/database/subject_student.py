from .__db_session import sa, SqlAlchemyBase, Table


class SubjectStudent(SqlAlchemyBase, Table):
    __tablename__ = 'subjects_students'
    fields = ['year', 'subject', 'student']

    year = sa.Column(sa.Integer, nullable=False, primary_key=True)
    subject = sa.Column(sa.Integer, nullable=False, primary_key=True)
    student = sa.Column(sa.Integer, nullable=False, primary_key=True)

    # Table

    @classmethod
    def select_by_year(cls, year: int) -> list:
        return cls.__select_by_expr__(cls.year == year)

    @classmethod
    def select_by_student(cls, year: int, student: int) -> list:
        return cls.__select_by_expr__(cls.year == year, cls.student == student)

    @classmethod
    def select_by_subject(cls, year: int, subject: int) -> list:
        return cls.__select_by_expr__(cls.year == year, cls.subject == subject)

    @classmethod
    def select_by_all(cls, year: int, subject: int, student: int):
        return cls.__select_by_expr__(cls.year == year, cls.subject == subject, cls.student == student, one=True)

    @classmethod
    def delete(cls, subject_student) -> None:
        return cls.__delete_by_expr__(cls.year == subject_student.year, cls.subject == subject_student.subject, cls.student == subject_student.student)

    @classmethod
    def delete_by_year(cls, year: int) -> None:
        return cls.__delete_by_expr__(cls.year == year)
