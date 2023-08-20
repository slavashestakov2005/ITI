from .__db_session import sa, SqlAlchemyBase, Table


class Team(SqlAlchemyBase, Table):
    __tablename__ = 'team'
    fields = ['id', 'name', 'iti_id', 'vertical']

    id = sa.Column(sa.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=False)
    iti_id = sa.Column(sa.Integer, nullable=False)
    vertical = sa.Column(sa.String, nullable=False)

    @staticmethod
    def sort_by_latter(team):
        return team.vertical

    # Table

    @classmethod
    def select_by_iti(cls, iti_id: int) -> list:
        return cls.__select_by_expr__(cls.iti_id == iti_id)

    @classmethod
    def select_by_iti_and_vertical(cls, iti_id: int, vertical: str):
        return cls.__select_by_expr__(cls.iti_id == iti_id, cls.vertical == vertical, one=True)

    @classmethod
    def delete_by_iti(cls, iti_id: int) -> None:
        return cls.__delete_by_expr__(cls.iti_id == iti_id)
