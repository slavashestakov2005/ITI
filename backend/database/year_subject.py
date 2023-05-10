from datetime import datetime
from .__db_session import sa, SqlAlchemyBase, Table


class YearSubject(SqlAlchemyBase, Table):
    __tablename__ = 'years_subjects'
    fields = ['year', 'subject', 'score_5', 'score_6', 'score_7', 'score_8', 'score_9', 'start', 'end', 'classes', 'place', 'n_d']

    year = sa.Column(sa.Integer, nullable=False, primary_key=True)
    subject = sa.Column(sa.Integer, nullable=False, primary_key=True)
    score_5 = sa.Column(sa.Integer, nullable=False)
    score_6 = sa.Column(sa.Integer, nullable=False)
    score_7 = sa.Column(sa.Integer, nullable=False)
    score_8 = sa.Column(sa.Integer, nullable=False)
    score_9 = sa.Column(sa.Integer, nullable=False)
    start = sa.Column(sa.Integer, nullable=False)
    end = sa.Column(sa.Integer, nullable=False)
    classes = sa.Column(sa.String, nullable=False)
    place = sa.Column(sa.String, nullable=False)
    n_d = sa.Column(sa.String, nullable=False)

    @staticmethod
    def sort_by_start(year_subject):
        return year_subject.start

    def date_str(self) -> str:
        return datetime.fromtimestamp(self.start).strftime('%Y-%m-%d')

    def start_str(self) -> str:
        return datetime.fromtimestamp(self.start).strftime('%H:%M')

    def end_str(self) -> str:
        return datetime.fromtimestamp(self.end).strftime('%H:%M')

    # Table

    @classmethod
    def select_by_year(cls, year: int) -> list:
        return cls.__select_by_expr__(cls.year == year)

    @classmethod
    def select(cls, year: int, subject: int):
        return cls.__select_by_expr__(cls.year == year, cls.subject == subject, one=True)

    @classmethod
    def update(cls, year_subject) -> None:
        return cls.__update_by_expr__(year_subject, cls.year == year_subject.year, cls.subject == year_subject.subject)

    @classmethod
    def delete_by_year(cls, year: int) -> None:
        return cls.__delete_by_expr__(cls.year == year)

    @classmethod
    def delete(cls, year: int, subject: int) -> None:
        return cls.__delete_by_expr__(cls.year == year, cls.subject == subject)
