from .__db_session import sa, SqlAlchemyBase, Table


class Result(SqlAlchemyBase, Table):
    __tablename__ = 'result'
    fields = ['iti_subject_id', 'student_code', 'student_id', 'result', 'net_score', 'position']

    iti_subject_id = sa.Column(sa.Integer, nullable=False, primary_key=True)
    student_code = sa.Column(sa.Integer, nullable=False, primary_key=True)
    student_id = sa.Column(sa.Integer, nullable=False)
    result = sa.Column(sa.Float, nullable=False)
    net_score = sa.Column(sa.Float, nullable=False)
    position = sa.Column(sa.Integer, nullable=False)

    @staticmethod
    def sort_by_result(result):
        return -result.result

    # Table

    @classmethod
    def select_by_iti_subject(cls, iti_subject_id: int) -> list:
        return cls.__select_by_expr__(cls.iti_subject_id == iti_subject_id)

    @classmethod
    def select_for_student(cls, student_id: int):
        return cls.__select_by_expr__(cls.student_id == student_id)

    @classmethod
    def select_for_student_code(cls, result):
        return cls.__select_by_expr__(cls.iti_subject_id == result.iti_subject_id,
                                      cls.student_code == result.student_code, one=True)

    @classmethod
    def update(cls, result) -> None:
        return cls.__update_by_expr__(result, cls.iti_subject_id == result.iti_subject_id,
                                      cls.student_code == result.student_code)

    @classmethod
    def delete_by_iti_subject(cls, iti_subject_id: int) -> None:
        return cls.__delete_by_expr__(cls.iti_subject_id == iti_subject_id)

    @classmethod
    def delete_by_student_code(cls, result) -> None:
        return cls.__delete_by_expr__(cls.iti_subject_id == result.iti_subject_id,
                                      cls.student_code == result.student_code)
