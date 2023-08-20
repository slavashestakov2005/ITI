from .__db_session import sa, SqlAlchemyBase, Table


class TeamConsent(SqlAlchemyBase, Table):
    __tablename__ = 'team_consent'
    fields = ['iti_id', 'student_id', 'status']

    iti_id = sa.Column(sa.Integer, nullable=False, primary_key=True)
    student_id = sa.Column(sa.Integer, nullable=False, primary_key=True)
    status = sa.Column(sa.Integer, nullable=False)

    # Table

    @classmethod
    def select_by_iti(cls, iti_id: int) -> list:
        return cls.__select_by_expr__(cls.iti_id == iti_id)

    @classmethod
    def select_approval_by_iti(cls, iti_id: int) -> list:
        return cls.__select_by_expr__(cls.iti_id == iti_id, cls.status == 1)

    @classmethod
    def select_rejection_by_iti(cls, iti_id: int) -> list:
        return cls.__select_by_expr__(cls.iti_id == iti_id, cls.status == -1)

    @classmethod
    def delete_by_iti(cls, iti_id: int) -> None:
        return cls.__delete_by_expr__(cls.iti_id == iti_id)

    @classmethod
    def delete(cls, iti_id: int, student_id: int) -> None:
        return cls.__delete_by_expr__(cls.iti_id == iti_id, cls.student_id == student_id)
