from .__db_session import sa, SqlAlchemyBase, Table


class Iti(SqlAlchemyBase, Table):
    __tablename__ = 'iti'
    fields = ['id', 'name_in_list', 'name_on_page', 'classes', 'ind_days', 'default_ind_score', 'net_score_formula',
              'ind_res_per_day', 'ind_prize_policy', 'automatic_division', 'auto_teams', 'sum_ind_to_team',
              'sum_gr_to_ind_policy', 'sum_gr_to_super', 'super_open_policy', 'students_in_team', 'encoding_type',
              'barcodes', 'description', 'block']

    id = sa.Column(sa.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    name_in_list = sa.Column(sa.String, nullable=False)
    name_on_page = sa.Column(sa.String, nullable=False)
    classes = sa.Column(sa.String, nullable=False)          # ordered (exm.: 56789, 234)
    ind_days = sa.Column(sa.Integer, nullable=False)
    default_ind_score = sa.Column(sa.Integer, nullable=False)
    net_score_formula = sa.Column(sa.Integer, nullable=False)
    ind_res_per_day = sa.Column(sa.Integer, nullable=False)
    ind_prize_policy = sa.Column(sa.Integer, nullable=False)
    automatic_division = sa.Column(sa.Integer, nullable=False)
    auto_teams = sa.Column(sa.String, nullable=False)       # use #sch-<n> for school-id n
    sum_ind_to_team = sa.Column(sa.Integer, nullable=False)
    sum_gr_to_ind_policy = sa.Column(sa.Integer, nullable=False)
    sum_gr_to_super = sa.Column(sa.Integer, nullable=False)
    super_open_policy = sa.Column(sa.Integer, nullable=False)
    students_in_team = sa.Column(sa.Integer, nullable=False)
    encoding_type = sa.Column(sa.Integer, nullable=False)
    barcodes = sa.Column(sa.Integer, nullable=False)
    description = sa.Column(sa.String, nullable=False)
    block = sa.Column(sa.Integer, nullable=False)

    def classes_list(self):
        return list(map(int, self.classes.split(' ')))
    
    def barcodes_start(self) -> int:
        parts = self.barcodes.split('-')
        if len(parts) != 2 or parts[0] == '' or parts[1] == '':
            raise ValueError("Диапазон штрих-кодов задан неправильно")
        return int(parts[0]) % 10 ** 12

    def barcodes_finish(self) -> int:
        parts = self.barcodes.split('-')
        if len(parts) != 2 or parts[0] == '' or parts[1] == '':
            raise ValueError("Диапазон штрих-кодов задан неправильно")
        return int(parts[1]) % 10 ** 12

    # TODO: change separator to ' | '
    def auto_teams_list(self):
        return self.auto_teams.split(' ')

    # Table
