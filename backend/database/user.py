from backend.database import Table, Row
from backend.database.team import TeamsTable
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


def is_in_team(year: int):
    return -10 * abs(year) - (2 if year < 0 else 0), -10 * abs(year) - (3 if year < 0 else 1)


class User(Row, UserMixin):
    """
        Строка таблицы UsersTable
        id          INT     NOT NULL    PK  AI  UNIQUE
        login       TEXT    NOT NULL            UNIQUE
        password    TEXT    NOT NULL
        status      INT     NOT NULL    -2 = 'full', -1 = 'admin', x = ...100100... (subjects)
        teams       TEXT    NOT NULL
    """
    fields = ['id', 'login', 'password', 'status', 'teams']

    def __init__(self, row):
        Row.__init__(self, User, row)

    def check_password(self, password) -> bool:
        if self.__is_none__:
            return False
        return check_password_hash(self.password, password)

    def set_password(self, password) -> None:
        if self.__is_none__:
            return
        self.password = generate_password_hash(password)

    def set_status(self, status: list) -> None:
        if '-1' in status:
            self.status = -1
        else:
            self.status = 0
            for now in status:
                self.status += 1 << int(now)

    def can_do(self, status: int):
        print('Can do ( ' + str(status) + ")")
        return self.status == -2 or \
               self.status == -1 and status != -2 or \
               status > 0 and (self.status >> status) % 2

    def teams_list(self, year: int):
        can = set(map(int, self.teams.split()))
        now = set([_.id for _ in TeamsTable.select_by_year(year)])
        now.add(is_in_team(year)[1])
        if self.can_do(-1):
            return now
        return list(can.intersection(now))

    def add_team(self, team: int):
        self.teams = ' '.join([str(team), *self.teams.split()])

    def delete_team(self, team: int):
        self.teams = ' '.join(set(self.teams.split()).symmetric_difference([str(team)]))

    def is_exists_team(self, team: int):
        return str(team) in self.teams.split()

    def subjects_str(self, subjects):
        if self.status < 0:
            return 'admin'
        t = ''
        for subject in subjects:
            if (self.status >> subject) % 2 == 1:
                t += subjects[subject] + '; '
        return t[:-2] or '—'


class UsersTable:
    table = "user"

    @staticmethod
    def create_table() -> None:
        Table.drop_and_create(UsersTable.table, '''(
        id	        INT NOT NULL UNIQUE KEY AUTO_INCREMENT,
        login	    VARCHAR(30) NOT NULL UNIQUE,
        password	TEXT NOT NULL,
        status	    INT NOT NULL,
        teams	    TEXT NOT NULL,
        PRIMARY KEY(id)
        )''')
        u = User([None, 'slava', '', -2, ''])
        u.set_password('123')
        UsersTable.insert(u)
        u = User([None, 'савокина', '', -1, ''])
        u.set_password('1')
        UsersTable.insert(u)
        u = User([None, 'проходский', '', -1, ''])
        u.set_password('1')
        UsersTable.insert(u)

    @staticmethod
    def select_all() -> list:
        return Table.select_list(UsersTable.table, User)

    @staticmethod
    def select_by_id(id: int) -> User:
        return Table.select_one(UsersTable.table, User, 'id', id)

    @staticmethod
    def select_by_login(login: str) -> User:
        return Table.select_one(UsersTable.table, User, 'login', login)

    @staticmethod
    def update_by_login(user: User) -> None:
        return Table.update(UsersTable.table, user, 'login')

    @staticmethod
    def insert(user: User) -> None:
        return Table.insert(UsersTable.table, user)

    @staticmethod
    def delete(user: User) -> None:
        return Table.delete(UsersTable.table, user)
