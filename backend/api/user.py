from flask_login import current_user
from flask_restful import reqparse, Resource

from ..api import api_group, api_item, ApiStatus
from ..database import ItiSubject, RoleGlobal, RoleIti, RoleItiSubject, User
from ..help import check_role, UserRoleGlobal, UserRoleIti, UserRoleItiSubject, UserRoleLogin
from ..queries.auto_generator import Generator


parser_login = reqparse.RequestParser()
parser_login.add_argument('password', required=True, type=str)
parser_login.add_argument('status', required=False, type=int, action='append', default=list)
parser_login.add_argument('login', required=True, type=str)
parser_type = reqparse.RequestParser()
parser_type.add_argument('type', required=True, type=str)
parser_password = reqparse.RequestParser()
parser_password.add_argument('password', required=True, type=str)
parser_password.add_argument('password_old', required=True, type=str)
parser_role_global = reqparse.RequestParser()
parser_role_global.add_argument('status', required=False, type=int, action='append', default=list)
parser_role_iti = reqparse.RequestParser()
parser_role_iti.add_argument('iti_id', required=True, type=int)
parser_role_iti.add_argument('status', required=False, type=int, action='append', default=list)
parser_role_iti_subject = reqparse.RequestParser()
parser_role_iti_subject.add_argument('iti_id', required=True, type=int)
parser_role_iti_subject.add_argument('status', required=False, type=int, action='append', default=list)
parser_role_iti_subject.add_argument('subjects', required=False, type=int, action='append', default=list)


def set_user_global_roles(user: User, roles: list[int]) -> bool:
    roles = sum(roles)
    sum_roles = 0
    for role in UserRoleGlobal:
        if role.value & roles == role.value:
            sum_roles |= role.value
            if not check_role(roles=[role]):
                return False
    data = RoleGlobal.build(user.id, sum_roles)
    if RoleGlobal.select(user.id) is None:
        RoleGlobal.insert(data)
    else:
        RoleGlobal.update(data)
    return True


def set_user_iti_roles(user: User, iti_id: int, roles: list[int]) -> bool:
    roles = sum(roles)
    sum_roles = 0
    for role in UserRoleIti:
        if role.value & roles == role.value:
            sum_roles |= role.value
            if not check_role(roles=[role], iti_id=iti_id):
                return False
    data = RoleIti.build(iti_id, user.id, sum_roles)
    if RoleIti.select(iti_id, user.id) is None:
        RoleIti.insert(data)
    else:
        RoleIti.update(data)
    return True


def set_user_iti_subject_roles(user: User, roles: list[int], iti_subject_ids: list[int], iti_id: int) -> bool:
    roles = sum(roles)
    for iti_subject_id in iti_subject_ids:
        for role in UserRoleItiSubject:
            if role.value & roles == role.value:
                if not check_role(roles=[role], iti_id=iti_id, iti_subject_id=iti_subject_id):
                    return False
    for ys in ItiSubject.select_by_iti(iti_id):
        RoleItiSubject.delete(ys.id, user.id)
    for iti_subject_id in iti_subject_ids:
        sum_roles = 0
        for role in UserRoleItiSubject:
            if role.value & roles == role.value:
                sum_roles |= role.value
        data = RoleItiSubject.build(iti_subject_id, user.id, sum_roles)
        RoleItiSubject.insert(data)
    return True


class UserResource(Resource):
    @api_item(db=User.select)
    def put(self, user: User):
        args = parser_type.parse_args()
        if args['type'] == 'role-global':
            args = parser_role_global.parse_args()
            if not check_role(roles=[UserRoleGlobal.CHANGE_USER]):
                return ApiStatus.ACCESS_DENIED, {}
            if not set_user_global_roles(user, args['status']):
                return ApiStatus.ACCESS_DENIED, {}
            Generator.gen_users_list()
        elif args['type'] == 'password':
            args = parser_password.parse_args()
            if not check_role(roles=[UserRoleLogin.LOGIN_LOCAL]):
                return ApiStatus.ACCESS_DENIED, {}
            if current_user.id != user.id:
                return ApiStatus.ACCESS_DENIED, {}
            if not current_user.check_password(args['password_old']):
                return ApiStatus.FAIL, {'message': 'Неверный старый пароль'}
            if not args['password']:
                return ApiStatus.FAIL, {'message': 'Новый пароль пустой'}
            user.set_password(args['password'])
            User.update(user)
        elif args['type'] == 'role-iti':
            args = parser_role_iti.parse_args()
            iti_id = args['iti_id']
            if not check_role(roles=[UserRoleGlobal.CHANGE_USER]):
                return ApiStatus.ACCESS_DENIED, {}
            if not check_role(roles=[UserRoleIti.ADMIN], iti_id=iti_id):
                return ApiStatus.ACCESS_DENIED, {}
            if not set_user_iti_roles(user, iti_id, args['status']):
                return ApiStatus.ACCESS_DENIED, {}
            Generator.gen_iti_users_list(iti_id)
        elif args['type'] == 'role-iti-subject':
            args = parser_role_iti_subject.parse_args()
            iti_id = args['iti_id']
            if not check_role(roles=[UserRoleGlobal.CHANGE_USER]):
                return ApiStatus.ACCESS_DENIED, {}
            if not check_role(roles=[UserRoleIti.ADMIN], iti_id=iti_id):
                return ApiStatus.ACCESS_DENIED, {}
            if not set_user_iti_subject_roles(user, args['status'], args['subjects'], iti_id):
                return ApiStatus.ACCESS_DENIED, {}
            Generator.gen_iti_users_list(iti_id)
        else:
            return ApiStatus.FAIL, {'message': 'Неизвестный тип запроса'}
        return ApiStatus.OK, {'message': 'Пользователь обновлён'}

    @api_item(db=User.select, roles=[UserRoleGlobal.CHANGE_USER])
    def delete(self, user: User):
        User.delete(user)
        Generator.gen_users_list()
        return ApiStatus.OK, {'message': 'Пользователь удалён'}


class UserListResource(Resource):
    @api_group(roles=[UserRoleGlobal.CHANGE_USER])
    def post(self):
        args = parser_login.parse_args()
        if User.select_by_login(args['login']):
            return ApiStatus.FAIL, {'message': 'Логин уже занят'}
        user = User.build(None, args['login'], args['password'], 0)
        user.set_password(args['password'])
        user_id = User.insert(user, return_id=True)
        user = User.select(user_id)
        set_user_global_roles(user, args['status'])
        Generator.gen_users_list()
        return ApiStatus.OK, {'message': 'Пользователь создан'}
