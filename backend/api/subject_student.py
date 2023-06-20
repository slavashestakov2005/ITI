from flask_restful import reqparse, Resource
from ..api import api_group
from ..database import SubjectStudent


parser_simple = reqparse.RequestParser()
parser_simple.add_argument('year', required=True, type=int)
parser_simple.add_argument('subject', required=False, type=str, action='append', default=list)
parser_simple.add_argument('old_subject', required=False, type=str, action='append', default=list)


# TODO: подумать над set.symmetric_difference, если пользователь не обновляет страничку


class SubjectStudentListResource(Resource):
    @api_group('admin')
    def post(self):
        args = parser_simple.parse_args()
        subjects = set(args['subject'])
        old_subjects = set(args['old_subject'])
        different = subjects.symmetric_difference(old_subjects)
        for x in different:
            t = x.split('_')
            t = SubjectStudent.build(args['year'], int(t[0]), int(t[1]))
            if x in subjects:
                SubjectStudent.insert(t)
            else:
                SubjectStudent.delete(t)
        return True, {'message': 'Сохранено'}
