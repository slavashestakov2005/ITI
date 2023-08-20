from .__db_session import sa, SqlAlchemyBase, Table


class ItiSubjectScore(SqlAlchemyBase, Table):
    __tablename__ = 'iti_subjects_scores'
    fields = ['iti_subject_id', 'class_n', 'max_value']

    iti_subject_id = sa.Column(sa.Integer, nullable=False, primary_key=True)
    class_n = sa.Column(sa.Integer, nullable=False, primary_key=True)
    max_value = sa.Column(sa.Integer, nullable=False)

    # Table

    @classmethod
    def select_by_iti_subject(cls, iti_subject_id: int) -> list:
        return cls.__select_by_expr__(cls.iti_subject_id == iti_subject_id)

    @classmethod
    def select(cls, iti_subject_id: int, class_n: int):
        return cls.__select_by_expr__(cls.iti_subject_id == iti_subject_id, cls.class_n == class_n, one=True)

    @classmethod
    def update(cls, iti_subject_score) -> None:
        return cls.__update_by_expr__(iti_subject_score, cls.iti_subject_id == iti_subject_score.iti_subject_id,
                                      cls.class_n == iti_subject_score.class_n)

    @classmethod
    def delete_by_iti_subject(cls, iti_subject_id: int) -> None:
        return cls.__delete_by_expr__(cls.iti_subject_id == iti_subject_id)

    @classmethod
    def delete(cls, iti_subject_id: int, class_n: int) -> None:
        return cls.__delete_by_expr__(cls.iti_subject_id == iti_subject_id, cls.class_n == class_n)
