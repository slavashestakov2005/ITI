from flask import request
from flask_restful import reqparse, Resource

from ..api import api_group, ApiStatus
from ..database import GroupResult, ItiSubject, Team
from ..help import check_role, UserRoleItiSubject


parser_simple = reqparse.RequestParser()
parser_simple.add_argument('year', required=True, type=int)
parser_simple.add_argument('subject', required=True, type=int)


class GroupResultListResource(Resource):
    @api_group()
    def post(self):
        args = parser_simple.parse_args()
        year, subject = args['year'], args['subject']
        iti_subject = ItiSubject.select(year, subject)
        if not iti_subject:
            return ApiStatus.FAIL, {'message': 'Такого предмета нет в этом году'}
        teams = Team.select_by_iti(year)
        for team in teams:
            try:
                gr = GroupResult.build(team.id, subject, float(request.json['score_' + str(team.id)]), 0)
            except Exception:
                return ApiStatus.FAIL, {'message': 'Некорректные данные'}
            if not GroupResult.select_by_team_and_subject(team.id, subject):
                if not check_role(roles=[UserRoleItiSubject.ADD_RESULT], iti_id=year, iti_subject_id=iti_subject.id):
                    return ApiStatus.ACCESS_DENIED, {}
                GroupResult.insert(gr)
            else:
                if not check_role(roles=[UserRoleItiSubject.EDIT_RESULT], iti_id=year, iti_subject_id=iti_subject.id):
                    return ApiStatus.ACCESS_DENIED, {}
                GroupResult.update(gr)
        return ApiStatus.OK, {'message': 'Результаты сохранены'}
