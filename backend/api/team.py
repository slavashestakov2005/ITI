from flask_restful import reqparse, Resource

from ..api import api_group, api_item, ApiStatus
from ..database import Team
from ..help import check_role, UserRoleIti
from ..queries.auto_generator import Generator


parser_simple = reqparse.RequestParser()
parser_simple.add_argument('name', required=True, type=str)
parser_simple.add_argument('latter', required=True, type=str)
parser_full = parser_simple.copy()
parser_full.add_argument('year', required=True, type=int)


class TeamResource(Resource):
    @api_item(db=Team.select)
    def put(self, team: Team):
        if not check_role(roles=[UserRoleIti.ADMIN], iti_id=team.iti_id):
            return ApiStatus.ACCESS_DENIED, {}
        args = parser_simple.parse_args()
        name, latter = args['name'], args['latter'].capitalize()
        if Team.select_by_iti_and_vertical(team.iti_id, latter):
            return ApiStatus.FAIL, {'message': 'Команда от этой вертикали уже есть'}
        new = Team.build(None, name, None, latter, allow_empty=True)
        team ^= new
        Team.update(team)
        Generator.gen_teams(team.iti_id)
        return ApiStatus.OK, {'message': 'Данные обновлены'}

    @api_item(db=Team.select)
    def delete(self, team: Team):
        if not check_role(roles=[UserRoleIti.ADMIN], iti_id=team.iti_id):
            return ApiStatus.ACCESS_DENIED, {}
        Team.delete(team)
        Generator.gen_teams(team.iti_id)
        return ApiStatus.OK, {'message': 'Команда удалена'}


class TeamListResource(Resource):
    @api_group()
    def post(self):
        args = parser_full.parse_args()
        year, name, latter = args['year'], args['name'], args['latter'].capitalize()
        if not check_role(roles=[UserRoleIti.ADMIN], iti_id=year):
            return ApiStatus.ACCESS_DENIED, {}
        if Team.select_by_iti_and_vertical(year, latter):
            return ApiStatus.FAIL, {'message': 'Команда от этой вертикали уже есть'}
        Team.insert(Team.build(None, name, year, latter))
        Generator.gen_teams(year)
        return ApiStatus.OK, {'message': 'Команда добавлена'}
