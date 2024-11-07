from datetime import datetime

from .__db_session import sa, SqlAlchemyBase, Table


class TgUser(SqlAlchemyBase, Table):
    __tablename__ = 'tg_user'
    id_field = 'telegram_id'
    fields = ['telegram_id', 'eljur_id', 'last_update', 'role']

    telegram_id = sa.Column(sa.Integer, nullable=False, unique=True, primary_key=True)
    eljur_id = sa.Column(sa.Integer, nullable=False)
    last_update = sa.Column(sa.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    role = sa.Column(sa.String, nullable=False)

    # Table
