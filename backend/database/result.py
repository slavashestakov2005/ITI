import sqlalchemy as sa
from .__db_session import SqlAlchemyBase, Table


class Result(SqlAlchemyBase, Table):
    __tablename__ = 'result'
    fields = ['year', 'subject', 'user', 'result', 'net_score', 'text_result', 'position']

    year = sa.Column(sa.Integer, nullable=False, primary_key=True)
    subject = sa.Column(sa.Integer, nullable=False, primary_key=True)
    user = sa.Column(sa.Integer, nullable=False, primary_key=True)
    result = sa.Column(sa.Float, nullable=False)
    net_score = sa.Column(sa.Float, nullable=False)
    text_result = sa.Column(sa.String, nullable=False)
    position = sa.Column(sa.Integer, nullable=False)

    @staticmethod
    def sort_by_result(result):
        return -result.result

    # Table
    @classmethod
    def select_by_year(cls, year: int) -> list:
        return cls.__select_by_expr__(cls.year == year)

    @classmethod
    def select_by_year_and_subject(cls, year: int, subject: int) -> list:
        return cls.__select_by_expr__(cls.year == year, cls.subject == subject)

    @classmethod
    def select_for_people(cls, result):
        return cls.__select_by_expr__(cls.year == result.year, cls.subject == result.subject, cls.user == result.user, one=True)

    @classmethod
    def update(cls, result) -> None:
        return cls.__update_by_expr__(result, cls.year == result.year, cls.subject == result.subject, cls.user == result.user)

    # @classmethod
    # def replace(results: list) -> None:
    #     i = 0
    #     while i < len(results):
    #         j = min(i + 125, len(results))
    #         Query.replace(ResultsTable.table, results[i:j])
    #         i = j

    @classmethod
    def delete_by_year(cls, year: int) -> None:
        return cls.__delete_by_expr__(cls.year == year)

    @classmethod
    def delete_by_people(cls, result) -> None:
        return cls.__delete_by_expr__(cls.year == result.year, cls.subject == result.subject, cls.user == result.user)
