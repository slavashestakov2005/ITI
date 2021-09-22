from ..database import History, HistoriesTable, User
from datetime import datetime
'''
    class Log            Работает с действиями пользователей.
        types/actions       Список для декодирования действий на английский/русский
        log(...)            Записывает действие в БД.
'''


class Log:
    types = ['result:save', 'result:update', 'result:delete']
    actions = ['Добавлен результат', 'Обновлен результат', 'Удален результат']

    @staticmethod
    def log(type: str, user: User, year: int, *args, subject=True):
        if subject:
            if not len(args):
                raise ValueError
            d = '; '.join(['@' + str(args[0]), *[str(_) for _ in args[1:]]])
        else:
            d = '; '.join([str(_) for _ in args])
        t = int(datetime.now().timestamp())
        h = History([None, year, t, user.id, Log.types.index(type), d, '0'])
        HistoriesTable.insert(h)
