from backend.database.database import *


class TeamStudent(Row):
    """
        Строка таблицы TeamsStudentsTable
        team        INT     NOT NULL    PK
        student     INT     NOT NULL    PK
    """
    fields = ['team', 'student']

    def __init__(self, row):
        Row.__init__(self, TeamStudent, row)


class TeamsStudentsTable:
    table = "teams_students"

    @staticmethod
    def create_table() -> None:
        DataBase.execute('''CREATE TABLE "''' + TeamsStudentsTable.table + '''" (
        "team"	INTEGER NOT NULL,
        "student"	INTEGER NOT NULL,
        PRIMARY KEY("team","student")
        );''')

    @staticmethod
    def select_all():
        return Table.select_all(TeamsStudentsTable.table, TeamStudent)

    @staticmethod
    def select_by_team(team: int) -> list:
        return Table.select_list_by_field(TeamsStudentsTable.table, 'team', team, TeamStudent)

    @staticmethod
    def select(team_student: TeamStudent) -> TeamStudent:
        return Table.select_by_fields(TeamsStudentsTable.table, TeamStudent, 'team', team_student.team, 'student',
                                      team_student.student)

    @staticmethod
    def insert(team_student: TeamStudent) -> None:
        return Table.insert_all_columns(TeamsStudentsTable.table, team_student)

    @staticmethod
    def delete(team_student: TeamStudent) -> None:
        return Table.delete_by_fields(TeamsStudentsTable.table, 'team', team_student.team, 'student',
               team_student.student)
