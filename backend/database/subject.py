from .__db_session import sa, SqlAlchemyBase, Table


class Subject(SqlAlchemyBase, Table):
    __tablename__ = 'subject'
    fields = ['id', 'name', 'short_name', 'type', 'diploma', 'msg']

    id = sa.Column(sa.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=False, unique=True)
    short_name = sa.Column(sa.String, nullable=False)
    type = sa.Column(sa.String, nullable=False)
    diploma = sa.Column(sa.String, nullable=False)
    msg = sa.Column(sa.String, nullable=False)

    def type_str(self):
        if self.type == 'i':
            return 'individual'
        elif self.type == 'g':
            return 'group'
        return 'team'

    def diplomas_br(self):
        return self.diploma.replace('\n', '<br>')

    def msg_br(self):
        return self.msg.replace('\n', '<br>')

    @staticmethod
    def sort_by_type(subject):
        if subject.type == 'i':
            return 0, subject.id
        elif subject.type == 'g':
            return 1, subject.id
        elif subject.type == 'a':
            return 2, subject.id
        else:
            return -1, -subject.id

    # Table
    @classmethod
    def select_by_name(cls, name: str):
        return cls.__select_by_expr__(cls.name == name, one=True)
