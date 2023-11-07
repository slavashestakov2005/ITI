from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .__db_session import sa, SqlAlchemyBase, Table
from .team import Team


class User(SqlAlchemyBase, UserMixin, Table):
    __tablename__ = 'user'
    fields = ['id', 'login', 'password', 'status']

    id = sa.Column(sa.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    login = sa.Column(sa.String, nullable=False, unique=True)
    password = sa.Column(sa.String, nullable=False)
    status = sa.Column(sa.String, nullable=False)      # -2 = 'full', -1 = 'admin', x = ...100100... (subjects)

    def check_password(self, password) -> bool:
        return check_password_hash(self.password, password)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def set_status(self, status: list) -> None:
        if '-2' in status:
            self.status = '-2'
        elif '-1' in status:
            self.status = '-1'
        else:
            self.status = ' '.join(map(str, sorted(status)))

    def can_do(self, status: int):
        status = str(status)
        return self.status == '-2' or \
               self.status == '-1' and status != '-2' or \
               str(status) in self.status

    def teams_list(self, year: int):
        return [_.id for _ in Team.select_by_iti(year)] if self.can_do(-1) else []

    def subjects_str(self, subjects):
        if '-2' in self.status:
            return 'full'
        if '-1' in self.status:
            return 'admin'
        t = ''
        for subject in self.status.split(' '):
            if subject:
                t += subjects[int(subject)] + '; '
        return t[:-2] or '—'

    # Table

    @classmethod
    def select_by_login(cls, login: str):
        return cls.__select_by_expr__(cls.login == login, one=True)

    @classmethod
    def update_by_login(cls, user) -> None:
        return cls.__update_by_expr__(user, cls.login == user.login)
