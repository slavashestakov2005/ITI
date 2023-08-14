from .__db_session import sa, SqlAlchemyBase, Table


class Barcode(SqlAlchemyBase, Table):
    __tablename__ = 'barcode'
    fields = ['year', 'code', 'student_id']

    year = sa.Column(sa.Integer, nullable=False, primary_key=True)
    code = sa.Column(sa.Integer, nullable=False, primary_key=True)
    student_id = sa.Column(sa.Integer, nullable=False)

    # Table

    @classmethod
    def select(cls, year: int, code: int):
        return cls.__select_by_expr__(cls.year == year, cls.code == code, one=True)

    @classmethod
    def delete(cls, barcode) -> None:
        return cls.__delete_by_expr__(cls.year == barcode.year, cls.code == barcode.code)
