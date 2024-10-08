from flask_restful import reqparse, Resource

from ..api import api_group, ApiStatus
from ..database import Student, Team, TeamConsent, TeamStudent
from ..help import check_role, UserRoleIti


parser_simple = reqparse.RequestParser()
parser_simple.add_argument('team', required=True, type=int)
parser_simple.add_argument('student', required=True, type=int)

parser_checkboxes = reqparse.RequestParser()
parser_checkboxes.add_argument('iti_id', required=True, type=int)
parser_checkboxes.add_argument('old', required=False, type=int, action='append', default=list)
parser_checkboxes.add_argument('new +', required=False, type=int, action='append', default=list)
parser_checkboxes.add_argument('new -', required=False, type=int, action='append', default=list)


class TeamStudentListResource(Resource):
    @api_group()
    def put(self):
        args = parser_checkboxes.parse_args()
        iti_id, old, new_plus, new_minus = args['iti_id'], args['old'], args['new +'], args['new -']
        if not check_role(roles=[UserRoleIti.ADMIN], iti_id=iti_id):
            return ApiStatus.ACCESS_DENIED, {}
        for student_id in old:
            TeamConsent.delete(iti_id, student_id)
        for student_id in new_plus:
            TeamConsent.insert(TeamConsent.build(iti_id, student_id, 1))
        for student_id in new_minus:
            TeamConsent.insert(TeamConsent.build(iti_id, student_id, -1))
        return ApiStatus.OK, {'message': 'Данные сохранены'}

    @api_group()
    def post(self):
        args = parser_simple.parse_args()
        team, student = Team.select(args['team']), Student.select(args['student'])
        if not team:
            return ApiStatus.FAIL, {'message': 'Такой команды нет'}
        if not student:
            return ApiStatus.FAIL, {'message': 'Такого участника нет'}
        if not check_role(roles=[UserRoleIti.ADMIN], iti_id=team.iti_id):
            return ApiStatus.ACCESS_DENIED, {}
        ts = TeamStudent.build(team.id, student.id)
        if TeamStudent.select(ts):
            return ApiStatus.FAIL, {'message': 'Этот участник уже в этой команде'}
        TeamStudent.insert(ts)
        return ApiStatus.OK, {'message': 'Участник добавлен'}

    @api_group()
    def delete(self):
        args = parser_simple.parse_args()
        team, student = Team.select(args['team']), Student.select(args['student'])
        if not team:
            return ApiStatus.FAIL, {'message': 'Такой команды нет'}
        if not student:
            return ApiStatus.FAIL, {'message': 'Такого участника нет'}
        if not check_role(roles=[UserRoleIti.ADMIN], iti_id=team.iti_id):
            return ApiStatus.ACCESS_DENIED, {'message': 'Доступ запрещён'}
        ts = TeamStudent.build(team.id, student.id)
        if not TeamStudent.select(ts):
            return ApiStatus.FAIL, {'message': 'Этого человека нет в этой команде'}
        TeamStudent.delete(ts)
        return ApiStatus.OK, {'message': 'Участник удалён'}
