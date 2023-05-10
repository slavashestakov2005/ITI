from .__db_session import sa, SqlAlchemyBase, Table


class Year(SqlAlchemyBase, Table):
    __tablename__ = 'year'
    fields = ['year', 'block']

    year = sa.Column(sa.Integer, nullable=False, unique=True, primary_key=True)
    block = sa.Column(sa.Integer, nullable=False)

    # Table

    @classmethod
    def default_init(cls):
        cls.insert(cls.build(2019, 1))
        cls.insert(cls.build(2020, 1))

    @classmethod
    def delete(cls, year: int) -> None:
        return cls.__delete_by_expr__(cls.year == year)
