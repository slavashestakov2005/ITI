from .__db_session import sa, SqlAlchemyBase, Table


class YearSubjectScore(SqlAlchemyBase, Table):
    __tablename__ = 'years_subjects_scores'
    fields = ['year_subject_id', 'class_n', 'max_value']

    year_subject_id = sa.Column(sa.Integer, nullable=False, primary_key=True)
    class_n = sa.Column(sa.Integer, nullable=False, primary_key=True)
    max_value = sa.Column(sa.Integer, nullable=False)

    # Table

    @classmethod
    def select_by_year_subject(cls, year_subject_id: int) -> list:
        return cls.__select_by_expr__(cls.year_subject_id == year_subject_id)

    @classmethod
    def select(cls, year_subject_id: int, class_n: int):
        return cls.__select_by_expr__(cls.year_subject_id == year_subject_id, cls.class_n == class_n, one=True)

    @classmethod
    def update(cls, year_subject_score) -> None:
        return cls.__update_by_expr__(year_subject_score, cls.year_subject_id == year_subject_score.year_subject_id,
                                      cls.class_n == year_subject_score.class_n)

    @classmethod
    def delete_by_year_subject(cls, year_subject_id: int) -> None:
        return cls.__delete_by_expr__(cls.year_subject_id == year_subject_id)

    @classmethod
    def delete(cls, year_subject_id: int, class_n: int) -> None:
        return cls.__delete_by_expr__(cls.year_subject_id == year_subject_id, cls.class_n == class_n)
