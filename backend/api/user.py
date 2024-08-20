from flask_login import current_user
from flask_restful import reqparse, Resource

from ..api import api_item, api_group
from ..database import User
from ..queries.auto_generator import Generator


parser_simple = reqparse.RequestParser()
parser_simple.add_argument('password', required=True, type=str)
parser_simple.add_argument('status', required=False, type=str, action='append', default=list)
parser_login = parser_simple.copy()
parser_login.add_argument('login', required=True, type=str)
parser_type = parser_simple.copy()
parser_type.add_argument('type', required=True, type=str)
parser_type.add_argument('password_old', required=True, type=str)


class UserResource(Resource):
    @api_item(User.select, 'login')
    def put(self, user: User):
        args = parser_type.parse_args()
        if args['type'] == 'status':
            if not current_user.can_do(-1):
                return False, {'message': 'Доступ запрещён'}
            user.set_status(args['status'])
        elif args['type'] == 'password':
            if current_user.id != user.id:
                return False, {'message': 'Доступ запрещён'}
            if not current_user.check_password(args['password_old']):
                return False, {'message': 'Неверный старый пароль'}
            if not args['password']:
                return False, {'message': 'Новый пароль пустой'}
            user.set_password(args['password'])
        else:
            return False, {'message': 'Неизвестный тип запроса'}
        User.update(user)
        Generator.gen_users_list()
        return True, {'message': 'Пользователь обновлён'}

    @api_item(User.select, 'admin')
    def delete(self, user: User):
        User.delete(user)
        Generator.gen_users_list()
        return True, {'message': 'Пользователь удалён'}


class UserListResource(Resource):
    @api_group('admin')
    def post(self):
        args = parser_login.parse_args()
        if User.select_by_login(args['login']):
            return False, {'message': 'Логин уже занят'}
        user = User.build(None, args['login'], args['password'], 0)
        user.set_password(args['password'])
        user.set_status(args['status'])
        User.insert(user)
        Generator.gen_users_list()
        return True, {'message': 'Пользователь создан'}
