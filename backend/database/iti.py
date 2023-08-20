from .__db_session import sa, SqlAlchemyBase, Table


class Iti(SqlAlchemyBase, Table):
    __tablename__ = 'iti'
    fields = ['id', 'name_in_list', 'name_on_page', 'classes', 'ind_days', 'default_ind_score', 'net_score_formula',
              'sum_ind_to_rating', 'automatic_division', 'auto_teams', 'sum_ind_to_team', 'teams_count',
              'students_in_team', 'description', 'block']

    id = sa.Column(sa.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    name_in_list = sa.Column(sa.String, nullable=False)
    name_on_page = sa.Column(sa.String, nullable=False)
    classes = sa.Column(sa.String, nullable=False)          # ordered (exm.: 56789, 234)
    ind_days = sa.Column(sa.Integer, nullable=False)
    default_ind_score = sa.Column(sa.Integer, nullable=False)
    net_score_formula = sa.Column(sa.Integer, nullable=False)
    sum_ind_to_rating = sa.Column(sa.Integer, nullable=False)
    automatic_division = sa.Column(sa.Integer, nullable=False)
    auto_teams = sa.Column(sa.String, nullable=False)
    sum_ind_to_team = sa.Column(sa.Integer, nullable=False)
    teams_count = sa.Column(sa.Integer, nullable=False)
    students_in_team = sa.Column(sa.Integer, nullable=False)
    description = sa.Column(sa.String, nullable=False)
    block = sa.Column(sa.Integer, nullable=False)

    def class_cnt(self):
        return len(self.classes)

    def class_min(self):
        return int(self.classes[0])

    # Table

    @classmethod
    def default_init(cls):
        cls.insert(cls.build(None, 'ИТИ ОШ-2019', 'ИТИ-2019', '56789', 2, 30, 0, 2, 0, '', 1, 8, 5,
                             'Только призовые места, дизайн №1', 1))
        cls.insert(cls.build(None, 'ИТИ ОШ-2020', 'ИТИ-2020', '56789', 2, 30, 0, 2, 0, '', 1, 8, 4,
                             'Только призовые места, дизайн №1', 1))
