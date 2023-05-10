from .__db_session import sa, SqlAlchemyBase, Table


class Team(SqlAlchemyBase, Table):
    __tablename__ = 'team'
    fields = ['id', 'name', 'year', 'later']

    id = sa.Column(sa.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=False)
    year = sa.Column(sa.Integer, nullable=False)
    later = sa.Column(sa.String, nullable=False)

    @staticmethod
    def sort_by_later(team):
        return team.later

    # Table

    @classmethod
    def select_by_year(cls, year: int) -> list:
        return cls.__select_by_expr__(cls.year == year)

    @classmethod
    def select_by_year_and_later(cls, year: int, later: str):
        return cls.__select_by_expr__(cls.year == year, cls.later == later, one=True)

    @classmethod
    def delete_by_year(cls, year: int) -> None:
        return cls.__delete_by_expr__(cls.year == year)
