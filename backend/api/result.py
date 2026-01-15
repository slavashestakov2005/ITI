from flask_login import current_user
from flask_restful import reqparse, Resource

from ..api import api_group, ApiStatus
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
        answer = save_result_(current_user, args['year'], args['subject'], args['code'], args['result'])
        max_allowed = None
        code = answer
        if isinstance(answer, tuple):
            code, max_allowed = answer
        if code == -1:
            return ApiStatus.ACCESS_DENIED, {}
        elif code == 1:
            return ApiStatus.FAIL, {'message': 'Поля не заполнены'}
        elif code == 2:
            return ApiStatus.FAIL, {'message': 'Такого кода нет'}
        elif code == 3:
            return ApiStatus.FAIL, {'message': 'Такого предмета нет в этом году'}
        elif code == 4:
            return ApiStatus.FAIL, {'message': 'Результат участника {0} уже сохранён. Для изменения необходимы права'
                                               'администратора'.format(args['code'])}
        elif code == 5:
            return ApiStatus.FAIL, {'message': 'Некорректные данные'}
        elif code == 6:
            msg = 'Сумма баллов больше допустимого'
            if max_allowed is not None:
                msg += f' (максимум {max_allowed})'
            return ApiStatus.FAIL, {'message': msg}
        elif code == 7:
            return ApiStatus.FAIL, {'message': 'Нет такого ИТИ'}
        elif code == 8:
            return ApiStatus.FAIL, {'message': 'По штрих-коду {0} результат уже сохранён в другом предмете'.format(args['code'])}
        elif code == 0:
            return ApiStatus.OK, {'message': 'Результат участника {0} сохранён'.format(args['code'])}

    @api_group()
    def delete(self):
        args = parser_simple.parse_args()
        ys = ItiSubject.select(args['year'], args['subject'])
        if not ys:
            return ApiStatus.FAIL, {'message': 'Предмет не найден для этого года'}
        code = delete_result_(current_user, ys.iti_id, ys.id, args['code'])
        if code == -1:
            return ApiStatus.ACCESS_DENIED
        elif code == 1:
            return ApiStatus.FAIL, {'message': 'Для данных предмета и участника не сохранён результат'}
        elif code == 0:
            return ApiStatus.OK, {'message': 'Удалено'}
