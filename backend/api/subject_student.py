from flask_restful import reqparse, Resource

from ..api import api_group
from ..database import IndDayStudent, ItiSubject, SubjectStudent


parser_simple = reqparse.RequestParser()
parser_simple.add_argument('year', required=True, type=int)
parser_simple.add_argument('subject', required=False, type=str, action='append', default=list)
parser_simple.add_argument('old_subject', required=False, type=str, action='append', default=list)


class SubjectStudentListResource(Resource):
    @api_group('admin')
    def post(self):
        args = parser_simple.parse_args()
        subjects = set(args['subject'])
        old_subjects = set(args['old_subject'])
        different = subjects.symmetric_difference(old_subjects)
        iti_subjects = {_.subject_id: _ for _ in ItiSubject.select_by_iti(args['year'])}
        for x in different:
            t = x.split('_')
            sub, stud = int(t[0]), int(t[1])
            if sub > 0:
                t = SubjectStudent.build(iti_subjects[sub].id, stud)
                if x in subjects:
                    SubjectStudent.insert(t)
                else:
                    SubjectStudent.delete(t)
            else:
                t = IndDayStudent.build(args['year'], -sub, stud)
                if x in subjects:
                    IndDayStudent.insert(t)
                else:
                    IndDayStudent.delete(t)
        return True, {'message': 'Сохранено'}
