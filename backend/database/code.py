from .__db_session import sa, SqlAlchemyBase, Table


class Code(SqlAlchemyBase, Table):
    __tablename__ = 'code'
    fields = ['iti_id', 'student_id', 'code']

    iti_id = sa.Column(sa.Integer, nullable=False, primary_key=True)
    student_id = sa.Column(sa.Integer, nullable=False, primary_key=True)
    code = sa.Column(sa.Integer, nullable=False)

    # Table

    @classmethod
    def select(cls, iti_id: int, code: int):
        return cls.__select_by_expr__(cls.iti_id == iti_id, cls.code == code, one=True)

    @classmethod
    def select_by_student(cls, iti_id: int, student_id: int):
        return cls.__select_by_expr__(cls.iti_id == iti_id, cls.student_id == student_id, one=True)

    @classmethod
    def select_by_iti(cls, iti_id: int) -> list:
        return cls.__select_by_expr__(cls.iti_id == iti_id)

    @classmethod
    def delete_by_iti(cls, iti_id: int) -> None:
        return cls.__delete_by_expr__(cls.iti_id == iti_id)
