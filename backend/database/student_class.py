from .__db_session import sa, SqlAlchemyBase, Table


class StudentClass(SqlAlchemyBase, Table):
    __tablename__ = 'students_classes'
    fields = ['student_id', 'iti_id', 'class_number', 'class_latter', 'school_id']

    student_id = sa.Column(sa.Integer, nullable=False, primary_key=True)
    iti_id = sa.Column(sa.Integer, nullable=False, primary_key=True)
    class_number = sa.Column(sa.Integer, nullable=False)
    class_latter = sa.Column(sa.String, nullable=False)
    school_id = sa.Column(sa.Integer, nullable=False)

    # Table

    @classmethod
    def select(cls, iti_id: int, student_id: int):
        return cls.__select_by_expr__(cls.student_id == student_id, cls.iti_id == iti_id, one=True)

    @classmethod
    def select_by_iti(cls, iti_id: int) -> list:
        return cls.__select_by_expr__(cls.iti_id == iti_id)

    @classmethod
    def update(cls, sc) -> None:
        return cls.__update_by_expr__(sc, cls.student_id == sc.student_id, cls.iti_id == sc.iti_id)

    @classmethod
    def delete_by_iti(cls, iti_id: int) -> None:
        return cls.__delete_by_expr__(cls.iti_id == iti_id)

    @classmethod
    def delete_by_student(cls, student_id: int) -> None:
        return cls.__delete_by_expr__(cls.student_id == student_id)

    @classmethod
    def delete(cls, sc) -> None:
        return cls.__delete_by_expr__(cls.iti_id == sc.iti_id, cls.student_id == sc.student_id)
