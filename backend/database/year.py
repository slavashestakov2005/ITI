from .__db_session import sa, SqlAlchemyBase, Table


class Year(SqlAlchemyBase, Table):
    __tablename__ = 'year'
    fields = ['id', 'year', 'classes', 'ind_days', 'default_score', 'teams', 'students_in_team', 'sum_individual', 'block']
    id_field = 'year'

    id = sa.Column(sa.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    year = sa.Column(sa.Integer, nullable=False, unique=True)
    classes = sa.Column(sa.String, nullable=False)      # ordered (exm.: 56789, 234)
    ind_days = sa.Column(sa.Integer, nullable=False)
    default_score = sa.Column(sa.Integer, nullable=False)
    teams = sa.Column(sa.Integer, nullable=False)
    students_in_team = sa.Column(sa.Integer, nullable=False)
    sum_individual = sa.Column(sa.Integer, nullable=False)
    block = sa.Column(sa.Integer, nullable=False)

    def class_cnt(self):
        return len(self.classes)

    def class_min(self):
        return int(self.classes[0])

    # Table

    @classmethod
    def default_init(cls):
        cls.insert(cls.build(None, 2019, '56789', 2, 30, 8, 5, 1, 1))
        cls.insert(cls.build(None, 2020, '56789', 2, 30, 8, 4, 1, 1))
