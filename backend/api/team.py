from flask_restful import reqparse, Resource
from ..api import api_item, api_group
from ..database import Team
from ..queries.auto_generator import Generator


parser_simple = reqparse.RequestParser()
parser_simple.add_argument('name', required=True, type=str)
parser_simple.add_argument('later', required=True, type=str)
parser_full = parser_simple.copy()
parser_full.add_argument('year', required=True, type=int)


class TeamResource(Resource):
    @api_item(Team.select, 'admin')
    def put(self, team: Team):
        args = parser_simple.parse_args()
        name, later = args['name'], args['later'].capitalize()
        if Team.select_by_year_and_later(team.year, later):
            return False, {'message': 'Команда от этой вертикали уже есть'}
        new = Team.build(None, name, None, later, allow_empty=True)
        team ^= new
        Team.update(team)
        Generator.gen_teams(team.year)
        Generator.gen_teams_students(team.year)
        return True, {'message': 'Данные обновлены'}

    @api_item(Team.select, 'admin')
    def delete(self, team: Team):
        Team.delete(team)
        Generator.gen_teams(team.year)
        return True, {'message': 'Команда удалена'}


class TeamListResource(Resource):
    @api_group('admin')
    def post(self):
        args = parser_full.parse_args()
        print(args)
        year, name, later = args['year'], args['name'], args['later'].capitalize()
        if Team.select_by_year_and_later(year, later):
            return False, {'message': 'Команда от этой вертикали уже есть'}
        Team.insert(Team.build(None, name, year, later))
        Generator.gen_teams(year)
        return True, {'message': 'Команда добавлена'}
