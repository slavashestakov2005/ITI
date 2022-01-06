from ..database import History, HistoriesTable, User, UsersTable, SubjectsTable
from ..queries.help import tr_format
from ..queries.results_raw import save_result_, delete_result_
from .log import Log
'''
    class Logger            Работает с действиями пользователей.
        print()             Генерирует таблицу действий.
        revert(his, user)   Отменяет действие.
'''


class Logger:
    @staticmethod
    def print(year: int):
        txt = '\n'
        users = {_.id: _.login for _ in UsersTable.select_all()}
        subjects = {str(_.id): _.short_name for _ in SubjectsTable.select_all()}
        for history in HistoriesTable.select_by_year(year):
            if history.description[:1] == '@':
                sp = history.description.split('; ', 1)
                sp[0] = subjects[sp[0][1:]]
                history.description = '; '.join(sp)
            revert = '<a href="revert?i={}">Отменить</a>'.format(history.id) if not history.revert\
                else 'Отменено ' + users[int(history.revert)]
            txt += tr_format(history.time_str(), users[history.user], Log.actions[history.type], history.description,
                             revert, tabs=3)
        return txt + ' ' * 8

    @staticmethod
    def revert(history: History, user: User):
        d = history.description.split('; ')
        d[0] = d[0][1:]
        year = history.year
        if history.type == 0:
            code = delete_result_(user, year, int(d[0]), int(d[1]))
        elif history.type == 1:
            code = save_result_(user, year, int(d[0]), int(d[1]), d[2])
        elif history.type == 2:
            code = save_result_(user, year, int(d[0]), int(d[1]), d[2])
        if code == 0:
            history.rev()
