from flask_login import current_user
from flask_restful import reqparse, Resource

from ..api import api_group
from ..database import ItiSubject
from ..queries.results_raw import delete_result_, save_result_


parser_simple = reqparse.RequestParser()
parser_simple.add_argument('year', required=True, type=int)
parser_simple.add_argument('subject', required=True, type=int)
parser_simple.add_argument('code', required=True, type=int)
parser_full = parser_simple.copy()
parser_full.add_argument('result', required=True, type=str)


# TODO: переделать строку Сохранён результат больше 30
# TODO: переделать строку По этому штрих-коду результат уже сохранён
class ResultListResource(Resource):
    @api_group()
    def post(self):
        args = parser_full.parse_args()
        code = save_result_(current_user, args['year'], args['subject'], args['code'], args['result'])
        if code == -1:
            return False, {'message': 'Доступ запрещён'}
        elif code == 1:
            return False, {'message': 'Поля не заполнены'}
        elif code == 2:
            return False, {'message': 'Такого кода нет'}
        elif code == 3:
            return False, {'message': 'Такого предмета нет в этом году'}
        elif code == 4:
            return False, {'message': 'Результат участника {0} уже сохранён. Для изменения необходимы права'
                                      'администратора'.format(args['code'])}
        elif code == 5:
            return False, {'message': 'Некорректные данные'}
        elif code == 6:
            return False, {'message': 'Сумма баллов больше 30'}
        elif code == 7:
            return False, {'message': 'Нет такого ИТИ'}
        elif code == 8:
            return False, {'message': 'По штрих-коду {0} результат уже сохранён в другом предмете'.format(args['code'])}
        elif code == 0:
            return True, {'message': 'Результат участника {0} сохранён'.format(args['code'])}

    @api_group('admin')
    def delete(self):
        args = parser_simple.parse_args()
        ys = ItiSubject.select(args['year'], args['subject'])
        if not ys:
            return False, {'message': 'Предмет не найден для этого года'}
        code = delete_result_(current_user, ys.id, args['code'])
        if code == -1:
            return False, {'message': 'Доступ запрещён'}
        elif code == 1:
            return False, {'message': 'Для данных предмета и участника не сохранён результат'}
        elif code == 0:
            return True, {'message': 'Удалено'}
