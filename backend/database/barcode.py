from .__db_session import sa, SqlAlchemyBase, Table


class Barcode(SqlAlchemyBase, Table):
    __tablename__ = 'barcode'
    fields = ['iti_id', 'code', 'student_id']

    iti_id = sa.Column(sa.Integer, nullable=False, primary_key=True)
    code = sa.Column(sa.Integer, nullable=False, primary_key=True)
    student_id = sa.Column(sa.Integer, nullable=False)

    # Table

    @classmethod
    def select(cls, iti_id: int, code: int):
        return cls.__select_by_expr__(cls.iti_id == iti_id, cls.code == code, one=True)

    @classmethod
    def select_by_iti(cls, iti_id: int):
        return cls.__select_by_expr__(cls.iti_id == iti_id)

    @classmethod
    def delete(cls, barcode) -> None:
        return cls.__delete_by_expr__(cls.iti_id == barcode.iti_id, cls.code == barcode.code)

    @classmethod
    def delete_by_iti(cls, iti_id: int):
        return cls.__delete_by_expr__(cls.iti_id == iti_id)
