from .__db_session import sa, SqlAlchemyBase, Table


class StudentEljur(SqlAlchemyBase, Table):
    __tablename__ = 'student_eljur'
    fields = ['student_id', 'eljur_id']

    student_id = sa.Column(sa.Integer, nullable=False, unique=True)
    eljur_id = sa.Column(sa.Integer, nullable=False, unique=True, primary_key=True)

    # Table

    @classmethod
    def select_by_eljur(cls, eljur_id: int):
        return cls.__select_by_expr__(cls.eljur_id == eljur_id, one=True)
