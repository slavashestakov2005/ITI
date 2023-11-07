from .__db_session import sa, SqlAlchemyBase, Table


class ItiSubject(SqlAlchemyBase, Table):
    __tablename__ = 'iti_subjects'
    fields = ['id', 'iti_id', 'subject_id', 'start', 'end', 'classes', 'place', 'n_d']

    id = sa.Column(sa.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    iti_id = sa.Column(sa.Integer, nullable=False)
    subject_id = sa.Column(sa.Integer, nullable=False)
    start = sa.Column(sa.Integer, nullable=False)
    end = sa.Column(sa.Integer, nullable=False)
    classes = sa.Column(sa.String, nullable=False)
    place = sa.Column(sa.String, nullable=False)
    n_d = sa.Column(sa.Integer, nullable=False)

    @staticmethod
    def sort_by_start(year_subject):
        return year_subject.start

    # Table

    @classmethod
    def select_by_id(cls, id_: int):
        return cls.__select_by_expr__(cls.id == id_, one=True)

    @classmethod
    def select_by_iti(cls, iti_id: int) -> list:
        return cls.__select_by_expr__(cls.iti_id == iti_id)

    @classmethod
    def select(cls, iti_id: int, subject_id: int):
        return cls.__select_by_expr__(cls.iti_id == iti_id, cls.subject_id == subject_id, one=True)

    @classmethod
    def update(cls, year_subject) -> None:
        return cls.__update_by_expr__(year_subject, cls.iti_id == year_subject.iti_id,
                                      cls.subject_id == year_subject.subject_id)

    @classmethod
    def delete_by_iti(cls, iti_id: int) -> None:
        return cls.__delete_by_expr__(cls.iti_id == iti_id)

    @classmethod
    def delete(cls, iti_id: int, subject_id: int) -> None:
        return cls.__delete_by_expr__(cls.iti_id == iti_id, cls.subject_id == subject_id)
