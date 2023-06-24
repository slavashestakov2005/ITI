from flask_restful import reqparse, Resource
from ..api import api_group
from ..database import Student, Team, TeamStudent


parser_simple = reqparse.RequestParser()
parser_simple.add_argument('team', required=True, type=int)
parser_simple.add_argument('student', required=True, type=int)


class TeamStudentListResource(Resource):
    @api_group('admin')
    def post(self):
        args = parser_simple.parse_args()
        team, student = Team.select(args['team']), Student.select(args['student'])
        if not team:
            return False, {'message': 'Такой команды нет'}
        if not student:
            return False, {'message': 'Такого участника нет'}
        ts = TeamStudent.build(team.id, student.id)
        if TeamStudent.select(ts):
            return False, {'message': 'Этот участник уже в этой команде'}
        TeamStudent.insert(ts)
        return True, {'message': 'Участник добавлен'}

    @api_group('admin')
    def delete(self):
        args = parser_simple.parse_args()
        team, student = Team.select(args['team']), Student.select(args['student'])
        if not team:
            return False, {'message': 'Такой команды нет'}
        if not student:
            return False, {'message': 'Такого участника нет'}
        ts = TeamStudent.build(team.id, student.id)
        if not TeamStudent.select(ts):
            return False, {'message': 'Этого человека нет в этой команде'}
        TeamStudent.delete(ts)
        return True, {'message': 'Участник удалён'}
