from flask_restful import reqparse, Resource

from ..api import api_item, api_group
from ..database import School


parser_simple = reqparse.RequestParser()
parser_simple.add_argument('name', required=True, type=str)
parser_simple.add_argument('short_name', required=True, type=str)


class SchoolResource(Resource):
    @api_item(School.select, 'admin')
    def put(self, school: School):
        args = parser_simple.parse_args()
        new = School.build(None, args['name'], args['short_name'], allow_empty=True)
        school ^= new
        School.update(school)
        return True, {'message': 'Школа обновлена'}

    @api_item(School.select, 'admin')
    def delete(self, school: School):
        School.delete(school)
        return True, {'message': 'Школа удалена'}


class SchoolListResource(Resource):
    @api_group('admin')
    def post(self):
        args = parser_simple.parse_args()
        school = School.build(None, args['name'], args['short_name'])
        School.insert(school)
        return True, {'message': 'Школа создана'}
