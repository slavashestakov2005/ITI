from flask import request
from flask_login import current_user
from flask_restful import reqparse, Resource
from ..api import api_group
from ..database import GroupResult, Team, YearSubject


parser_simple = reqparse.RequestParser()
parser_simple.add_argument('year', required=True, type=int)
parser_simple.add_argument('subject', required=True, type=int)


class GroupResultListResource(Resource):
    @api_group()
    def post(self):
        print('start')
        args = parser_simple.parse_args()
        year, subject = args['year'], args['subject']
        if not current_user.can_do(subject):
            return False, {'message': 'Доступ запрещён'}
        if not YearSubject.select(year, subject):
            return False, {'message': 'Такого предмета нет в этом году'}
        teams = Team.select_by_year(year)
        for team in teams:
            try:
                gr = GroupResult.build(team.id, subject, int(request.json['score_' + str(team.id)]))
            except Exception:
                return False, {'message': 'Некорректные данные'}
            if not GroupResult.select_by_team_and_subject(team.id, subject):
                GroupResult.insert(gr)
            else:
                GroupResult.update(gr)
        return True, {'message': 'Результаты сохранены'}
