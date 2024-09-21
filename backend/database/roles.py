from .__db_session import sa, SqlAlchemyBase, Table


class RoleGlobal(SqlAlchemyBase, Table):
    __tablename__ = 'role_global'
    fields = ['user_id', 'role']
    id_field = 'user_id'

    user_id = sa.Column(sa.Integer, sa.ForeignKey('user.id'), nullable=False, unique=True, primary_key=True)
    role = sa.Column(sa.Integer, nullable=False)


class RoleIti(SqlAlchemyBase, Table):
    __tablename__ = 'role_iti'
    fields = ['iti_id', 'user_id', 'role']

    iti_id = sa.Column(sa.Integer, nullable=False, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('user.id'), nullable=False, primary_key=True)
    role = sa.Column(sa.Integer, nullable=False)

    @classmethod
    def select(cls, iti_id: int, user_id: int):
        return cls.__select_by_expr__(cls.iti_id == iti_id, cls.user_id == user_id, one=True)

    @classmethod
    def select_by_iti(cls, iti_id: int):
        return cls.__select_by_expr__(cls.iti_id == iti_id)

    @classmethod
    def update(cls, row) -> None:
        return cls.__update_by_expr__(row, cls.iti_id == row.iti_id, cls.user_id == row.user_id)


class RoleItiSubject(SqlAlchemyBase, Table):
    __tablename__ = 'role_iti_subject'
    fields = ['iti_subject_id', 'user_id', 'role']

    iti_subject_id = sa.Column(sa.Integer, nullable=False, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('user.id'), nullable=False, primary_key=True)
    role = sa.Column(sa.Integer, nullable=False)

    @classmethod
    def select_by_iti_subject(cls, iti_subject_id: int):
        return cls.__select_by_expr__(cls.iti_subject_id == iti_subject_id)

    @classmethod
    def update(cls, row) -> None:
        return cls.__update_by_expr__(row, cls.iti_subject_id == row.iti_subject_id, cls.user_id == row.user_id)

    @classmethod
    def delete(cls, iti_subject_id: int, user_id: int):
        return cls.__delete_by_expr__(cls.iti_subject_id == iti_subject_id, cls.user_id == user_id)
