from backend.database import Row, Table, Query


class TeamStudent(Row):
    """
        Строка таблицы TeamsStudentsTable
        team        INT     NOT NULL    PK
        student     INT     NOT NULL    PK
    """
    fields = ['team', 'student']

    def __init__(self, row):
        Row.__init__(self, TeamStudent, row)


class TeamsStudentsTable(Table):
    table = "teams_students"
    row = TeamStudent
    create = '''(
        team	INT NOT NULL,
        student	INT NOT NULL,
        PRIMARY KEY(team,student)
        );'''

    @staticmethod
    def select_by_team(team: int) -> list:
        return Query.select_list(TeamsStudentsTable.table, TeamStudent, 'team', team)

    @staticmethod
    def select_by_student(student: int) -> list:
        return Query.select_list(TeamsStudentsTable.table, TeamStudent, 'student', student)

    @staticmethod
    def select(team_student: TeamStudent) -> TeamStudent:
        return Query.select_one(TeamsStudentsTable.table, TeamStudent, 'team', team_student.team, 'student',
                                team_student.student)

    @staticmethod
    def delete(team_student: TeamStudent) -> None:
        return Query.delete(TeamsStudentsTable.table, 'team', team_student.team, 'student', team_student.student)

    @staticmethod
    def delete_by_team(team: int) -> None:
        return Query.delete(TeamsStudentsTable.table, 'team', team)
