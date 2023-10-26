from .__db_session import sa, SqlAlchemyBase, Table


class GroupResult(SqlAlchemyBase, Table):
    __tablename__ = 'group_results'
    fields = ['team_id', 'subject_id', 'result', 'position']

    team_id = sa.Column(sa.Integer, nullable=False, primary_key=True)
    subject_id = sa.Column(sa.Integer, nullable=False, primary_key=True)
    result = sa.Column(sa.Integer, nullable=False)
    position = sa.Column(sa.Integer, nullable=False)

    @staticmethod
    def sort_by_result(result):
        return -result.result

    # Table

    @classmethod
    def select_by_team(cls, team_id: int) -> list:
        return cls.__select_by_expr__(cls.team_id == team_id)

    @classmethod
    def select_by_subject(cls, subject_id: int) -> list:
        return cls.__select_by_expr__(cls.subject_id == subject_id)

    @classmethod
    def select_by_team_and_subject(cls, team_id: int, subject_id: int):
        return cls.__select_by_expr__(cls.team_id == team_id, cls.subject_id == subject_id, one=True)

    @classmethod
    def update(cls, row) -> None:
        return cls.__update_by_expr__(row, cls.team_id == row.team_id, cls.subject_id == row.subject_id)

    @classmethod
    def delete_by_team(cls, team_id: int) -> None:
        return cls.__delete_by_expr__(cls.team_id == team_id)
