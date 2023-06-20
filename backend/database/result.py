from .__db_session import sa, SqlAlchemyBase, Table


class Result(SqlAlchemyBase, Table):
    __tablename__ = 'result'
    fields = ['year_subject', 'student_code', 'student_id', 'result', 'net_score', 'position']

    year_subject = sa.Column(sa.Integer, nullable=False, primary_key=True)
    student_code = sa.Column(sa.Integer, nullable=False, primary_key=True)
    student_id = sa.Column(sa.Integer, nullable=False)
    result = sa.Column(sa.Float, nullable=False)
    net_score = sa.Column(sa.Integer, nullable=False)
    position = sa.Column(sa.Integer, nullable=False)

    @staticmethod
    def sort_by_result(result):
        return -result.result

    # Table
    # @classmethod
    # def select_by_year(cls, year: int) -> list:
    #     return cls.__select_by_expr__(cls.year == year)

    @classmethod
    def select_by_year_subject(cls, year_subject: int) -> list:
        return cls.__select_by_expr__(cls.year_subject == year_subject)

    @classmethod
    def select_for_people(cls, result):
        return cls.__select_by_expr__(cls.year_subject == result.year_subject, cls.student_code == result.student_code,
                                      one=True)

    @classmethod
    def update(cls, result) -> None:
        return cls.__update_by_expr__(result, cls.year_subject == result.year_subject, cls.student_code == result.student_code)

    # @classmethod
    # def replace(cls, result) -> None:
    #     res = cls.select_for_people(result)
    #     if res is None:
    #         cls.insert(result)
    #     else:
    #         cls.update(result)

    @classmethod
    def delete_by_year_subject(cls, year_subject_id: int) -> None:
        return cls.__delete_by_expr__(cls.year_subject == year_subject_id)

    @classmethod
    def delete_by_people(cls, result) -> None:
        return cls.__delete_by_expr__(cls.year_subject == result.year_subject, cls.student_code == result.student_code)
