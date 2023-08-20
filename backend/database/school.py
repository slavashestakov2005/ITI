from .__db_session import sa, SqlAlchemyBase, Table


class School(SqlAlchemyBase, Table):
    __tablename__ = 'school'
    fields = ['id', 'name', 'short_name']

    id = sa.Column(sa.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=False)
    short_name = sa.Column(sa.String, nullable=False)

    # Table

    @classmethod
    def default_init(cls):
        cls.insert(cls.build(None, 'МАОУ «КУГ №1 - Универс»', 'Универс'))
