import json

from .__db_session import sa, SqlAlchemyBase, Table


class SuperGameResult(SqlAlchemyBase, Table):
    __tablename__ = 'super_game_result'
    fields = ['id', 'iti_id', 'teams', 'winner', 'is_draw', 'created_at']

    id = sa.Column(sa.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    iti_id = sa.Column(sa.Integer, nullable=False)
    teams = sa.Column(sa.Text, nullable=False)
    winner = sa.Column(sa.String, nullable=True)
    is_draw = sa.Column(sa.Boolean, nullable=False, default=False)
    created_at = sa.Column(sa.Integer, nullable=False)

    def teams_list(self) -> list:
        try:
            data = json.loads(self.teams)
        except Exception:
            return []
        return data if isinstance(data, list) else []

    # Table
    @classmethod
    def select_by_iti(cls, iti_id: int) -> list:
        return cls.__select_by_expr__(cls.iti_id == iti_id)
