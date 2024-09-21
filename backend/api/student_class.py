from flask_restful import Resource

from ..api import api_item, ApiStatus
from ..database import StudentClass
from ..help import UserRoleGlobal


class StudentClassResource(Resource):
    @api_item(db=StudentClass.select, roles=[UserRoleGlobal.CHANGE_STUDENT])
    def delete(self, sc: StudentClass):
        StudentClass.delete(sc)
        return ApiStatus.OK, {'message': 'Участник удалён из класса'}
