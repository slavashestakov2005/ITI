from backend.database.database import *


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


class TeamsTable:
    table = "team"

    @staticmethod
    def create_table() -> None:
        DataBase.execute('''CREATE TABLE "''' + TeamsTable.table + '''" (
        "id"	INTEGER NOT NULL UNIQUE,
        "name"	TEXT NOT NULL,
        "year"	INTEGER NOT NULL,
        "later"	TEXT NOT NULL,
        PRIMARY KEY("id" AUTOINCREMENT)
        );''')

    @staticmethod
    def select_all() -> list:
        return Table.select_all(TeamsTable.table, Team)

    @staticmethod
    def select_by_year(year: int) -> list:
        return Table.select_list_by_field(TeamsTable.table, 'year', year, Team)

    @staticmethod
    def select_by_year_and_later(year: int, later: str) -> Team:
        return Table.select_by_fields(TeamsTable.table, Team, 'year', year, 'later', later)

    @staticmethod
    def select_by_id(id: int) -> Team:
        return Table.select_by_field(TeamsTable.table, 'id', id, Team)

    @staticmethod
    def insert(team: Team) -> None:
        return Table.insert_all_columns(TeamsTable.table, team)

    @staticmethod
    def delete(team: Team) -> None:
        return Table.delete(TeamsTable.table, team)

