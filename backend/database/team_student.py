from .__db_session import sa, SqlAlchemyBase, Table


class TeamStudent(SqlAlchemyBase, Table):
    __tablename__ = 'teams_students'
    fields = ['team', 'student']

    team = sa.Column(sa.Integer, nullable=False, primary_key=True)
    student = sa.Column(sa.Integer, nullable=False, primary_key=True)

    # Table

    @classmethod
    def select_by_team(cls, team: int) -> list:
        return cls.__select_by_expr__(cls.team == team)

    @classmethod
    def select_by_student(cls, student: int) -> list:
        return cls.__select_by_expr__(cls.student == student)

    @classmethod
    def select(cls, team_student):
        return cls.__select_by_expr__(cls.team == team_student.team, cls.student == team_student.student, one=True)

    @classmethod
    def delete(cls, team_student) -> None:
        return cls.__delete_by_expr__(cls.team == team_student.team, cls.student == team_student.student)

    @classmethod
    def delete_by_team(cls, team: int) -> None:
        return cls.__delete_by_expr__(cls.team == team)
