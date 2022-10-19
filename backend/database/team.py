from backend.database import Row, Table, Query


class Team(Row):
    """
        Строка таблицы TeamsTable
        id      INT     NOT NULL    PK  AI  UNIQUE
        name    TEXT    NOT NULL
        year    INT     NOT NULL
        later   TEXT    NOT NULL
    """
    fields = ['id', 'name', 'year', 'later']

    def __init__(self, row):
        Row.__init__(self, Team, row)

    @staticmethod
    def sort_by_later(team):
        return team.later


class TeamsTable(Table):
    table = "team"
    row = Team
    create = '''(
        id      INT NOT NULL UNIQUE KEY AUTO_INCREMENT,
        name	TEXT NOT NULL,
        year	INT NOT NULL,
        later	TEXT NOT NULL,
        PRIMARY KEY(id)
        );'''

    @staticmethod
    def select_by_year(year: int) -> list:
        return Query.select_list(TeamsTable.table, Team, 'year', year)

    @staticmethod
    def select_by_year_and_later(year: int, later: str) -> Team:
        return Query.select_one(TeamsTable.table, Team, 'year', year, 'later', later)

    @staticmethod
    def delete_by_year(year: int) -> None:
        return Query.delete(TeamsTable.table, 'year', year)
