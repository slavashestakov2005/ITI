from .__db_session import create_session, sa, SqlAlchemyBase, Table


class StudentCode(SqlAlchemyBase, Table):
    __tablename__ = 'students_codes'
    fields = ['year', 'code1', 'code2', 'student']

    year = sa.Column(sa.Integer, nullable=False, primary_key=True)
    code1 = sa.Column(sa.Integer, nullable=False)
    code2 = sa.Column(sa.Integer, nullable=False)
    student = sa.Column(sa.Integer, nullable=False, primary_key=True)

    # Table

    @classmethod
    def select_by_year(cls, year: int) -> list:
        return cls.__select_by_expr__(cls.year == year)

    @classmethod
    def select_by_code(cls, year: int, code: int, day: int = None):
        if day > 1:
            day = 2
        if not day:
            return [cls.select_by_code(year, code, 1)]
        return cls.__select_by_expr__(cls.year == year, getattr(cls, 'code' + str(day)) == code, one=True)

    @classmethod
    def select_by_student(cls, year: int, student: int):
        return cls.__select_by_expr__(cls.year == year, cls.student == student, one=True)

    @staticmethod
    def insert_all(codes: list) -> None:
        session = create_session()
        for code in codes:
            session.add(code)
        session.commit()

    @classmethod
    def delete_by_year(cls, year: int) -> None:
        return cls.__delete_by_expr__(cls.year == year)
