from backend.database import Table, Row


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
        Table.drop_and_create(TeamsStudentsTable.table, '''(
        "team"	INTEGER NOT NULL,
        "student"	INTEGER NOT NULL,
        PRIMARY KEY("team","student")
        )''')

    @staticmethod
    def select_all() -> list:
        return Table.select_list(TeamsStudentsTable.table, TeamStudent)

    @staticmethod
    def select_by_team(team: int) -> list:
        return Table.select_list(TeamsStudentsTable.table, TeamStudent, 'team', team)

    @staticmethod
    def select(team_student: TeamStudent) -> TeamStudent:
        return Table.select_one(TeamsStudentsTable.table, TeamStudent, 'team', team_student.team, 'student',
                                team_student.student)

    @staticmethod
    def insert(team_student: TeamStudent) -> None:
        return Table.insert(TeamsStudentsTable.table, team_student)

    @staticmethod
    def delete(team_student: TeamStudent) -> None:
        return Table.delete(TeamsStudentsTable.table, 'team', team_student.team, 'student', team_student.student)
