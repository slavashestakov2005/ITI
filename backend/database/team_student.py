from .__db_session import sa, SqlAlchemyBase, Table


class TeamStudent(SqlAlchemyBase, Table):
    __tablename__ = 'teams_students'
    fields = ['team_id', 'student_id']

    team_id = sa.Column(sa.Integer, nullable=False, primary_key=True)
    student_id = sa.Column(sa.Integer, nullable=False, primary_key=True)

    # Table

    @classmethod
    def select_by_team(cls, team_id: int) -> list:
        return cls.__select_by_expr__(cls.team_id == team_id)

    @classmethod
    def select_by_student(cls, student_id: int) -> list:
        return cls.__select_by_expr__(cls.student_id == student_id)

    @classmethod
    def select(cls, team_student):
        return cls.__select_by_expr__(cls.team_id == team_student.team_id, cls.student_id == team_student.student_id,
                                      one=True)

    @classmethod
    def delete(cls, team_student) -> None:
        return cls.__delete_by_expr__(cls.team_id == team_student.team_id, cls.student_id == team_student.student_id)

    @classmethod
    def delete_by_team(cls, team_id: int) -> None:
        return cls.__delete_by_expr__(cls.team_id == team_id)
