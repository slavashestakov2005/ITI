from .__db_session import sa, SqlAlchemyBase, Table


class SubjectStudent(SqlAlchemyBase, Table):
    __tablename__ = 'subjects_students'
    fields = ['iti_subject_id', 'student_id']

    iti_subject_id = sa.Column(sa.Integer, nullable=False, primary_key=True)
    student_id = sa.Column(sa.Integer, nullable=False, primary_key=True)

    # Table

    @classmethod
    def select_by_subject(cls, iti_subject_id: int) -> list:
        return cls.__select_by_expr__(cls.iti_subject_id == iti_subject_id)

    @classmethod
    def select_by_all(cls, iti_subject_id: int, student_id: int):
        return cls.__select_by_expr__(cls.iti_subject_id == iti_subject_id, cls.student_id == student_id, one=True)

    @classmethod
    def delete(cls, subject_student) -> None:
        return cls.__delete_by_expr__(cls.iti_subject_id == subject_student.iti_subject_id,
                                      cls.student_id == subject_student.student_id)

    @classmethod
    def delete_by_iti_subject(cls, iti_subject_id: int) -> None:
        return cls.__delete_by_expr__(cls.iti_subject_id == iti_subject_id)
