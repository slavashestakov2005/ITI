from .__db_session import sa, SqlAlchemyBase, Table


class StudentClass(SqlAlchemyBase, Table):
    __tablename__ = 'students_classes'
    fields = ['student_id', 'year', 'class_number', 'class_latter']

    student_id = sa.Column(sa.Integer, nullable=False, primary_key=True)
    year = sa.Column(sa.Integer, nullable=False, primary_key=True)
    class_number = sa.Column(sa.Integer, nullable=False)
    class_latter = sa.Column(sa.String, nullable=False)

    # Table

    @classmethod
    def select(cls, year: int, student_id: int):
        return cls.__select_by_expr__(cls.student_id == student_id, cls.year == year, one=True)

    @classmethod
    def select_by_year(cls, year: int) -> list:
        return cls.__select_by_expr__(cls.year == year)

    @classmethod
    def update(cls, sc) -> None:
        return cls.__update_by_expr__(sc, cls.student_id == sc.student_id, cls.year == sc.year)

    @classmethod
    def delete_by_year(cls, year: int) -> None:
        return cls.__delete_by_expr__(cls.year == year)

    @classmethod
    def delete_by_student(cls, student_id: int) -> None:
        return cls.__delete_by_expr__(cls.student_id == student_id)

    @classmethod
    def delete(cls, sc) -> None:
        return cls.__delete_by_expr__(cls.year == sc.year, cls.student_id == sc.student_id)
