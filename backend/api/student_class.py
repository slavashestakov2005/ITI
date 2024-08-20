from flask_restful import Resource

from ..api import api_item
from ..database import StudentClass


class StudentClassResource(Resource):
    @api_item(StudentClass.select, 'admin')
    def delete(self, sc: StudentClass):
        StudentClass.delete(sc)
        return True, {'message': 'Участник удалён из класса'}
