from .__db_session import sa, SqlAlchemyBase, Table


class IndDayStudent(SqlAlchemyBase, Table):
    __tablename__ = 'ind_days_students'
    fields = ['iti_id', 'n_d', 'student_id']

    iti_id = sa.Column(sa.Integer, nullable=False, primary_key=True)
    n_d = sa.Column(sa.Integer, nullable=False, primary_key=True)
    student_id = sa.Column(sa.Integer, nullable=False, primary_key=True)

    # Table

    @classmethod
    def select_by_iti(cls, iti_id: int) -> list:
        return cls.__select_by_expr__(cls.iti_id == iti_id)

    @classmethod
    def select_by_iti_and_student(cls, iti_id: int, student_id: int) -> list:
        return cls.__select_by_expr__(cls.iti_id == iti_id, cls.student_id == student_id)

    @classmethod
    def delete(cls, ind_ds) -> None:
        return cls.__delete_by_expr__(cls.iti_id == ind_ds.iti_id, cls.n_d == ind_ds.n_d,
                                      cls.student_id == ind_ds.student_id)
