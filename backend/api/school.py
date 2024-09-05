from flask_restful import reqparse, Resource

from ..api import api_group, api_item, ApiStatus
from ..database import School
from ..help import UserRoleGlobal


parser_simple = reqparse.RequestParser()
parser_simple.add_argument('name', required=True, type=str)
parser_simple.add_argument('short_name', required=True, type=str)


class SchoolResource(Resource):
    @api_item(db=School.select, roles=[UserRoleGlobal.CHANGE_SCHOOL])
    def put(self, school: School):
        args = parser_simple.parse_args()
        new = School.build(None, args['name'], args['short_name'], allow_empty=True)
        school ^= new
        School.update(school)
        return ApiStatus.OK, {'message': 'Школа обновлена'}

    @api_item(db=School.select, roles=[UserRoleGlobal.CHANGE_SCHOOL])
    def delete(self, school: School):
        School.delete(school)
        return ApiStatus.OK, {'message': 'Школа удалена'}


class SchoolListResource(Resource):
    @api_group(roles=[UserRoleGlobal.CHANGE_SCHOOL])
    def post(self):
        args = parser_simple.parse_args()
        school = School.build(None, args['name'], args['short_name'])
        School.insert(school)
        return ApiStatus.OK, {'message': 'Школа создана'}
