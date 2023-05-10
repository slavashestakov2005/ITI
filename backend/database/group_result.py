from .__db_session import sa, SqlAlchemyBase, Table


class GroupResult(SqlAlchemyBase, Table):
    __tablename__ = 'group_results'
    fields = ['team', 'subject', 'result']

    team = sa.Column(sa.Integer, nullable=False, primary_key=True)
    subject = sa.Column(sa.Integer, nullable=False, primary_key=True)
    result = sa.Column(sa.Integer, nullable=False)

    @staticmethod
    def sort_by_result(result):
        return -result.result

    # Table

    @classmethod
    def select_by_team(cls, team: int) -> list:
        return cls.__select_by_expr__(cls.team == team)

    @classmethod
    def select_by_subject(cls, subject: int) -> list:
        return cls.__select_by_expr__(cls.subject == subject)

    @classmethod
    def select_by_team_and_subject(cls, team: int, subject: int):
        return cls.__select_by_expr__(cls.team == team, cls.subject == subject, one=True)

    @classmethod
    def update(cls, row) -> None:
        return cls.__update_by_expr__(row, cls.team == row.team, cls.subject == row.subject)

    @classmethod
    def delete_by_team(cls, team: int) -> None:
        return cls.__delete_by_expr__(cls.team == team)
