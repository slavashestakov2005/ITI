from flask_restful import reqparse, Resource

from ..api import api_item, api_group, str_or_int
from ..database import get_student_by_params, School, Student, StudentClass
from ..queries.auto_generator import Generator
from ..queries.help import split_class


parser_full = reqparse.RequestParser()
parser_full.add_argument('year', required=True, type=int)
parser_full.add_argument('class', required=True, type=str)
parser_full.add_argument('name1', required=True, type=str)
parser_full.add_argument('name2', required=True, type=str)
parser_full.add_argument('name3', required=False, type=str)
parser_full.add_argument('gender', required=True, type=str)
parser_full.add_argument('other_id', required=True, type=str)
parser_full.add_argument('school', required=True, type=str_or_int)


def parse_name(name1, name2, name3):
    if name3 is None:
        name3 = ''
    return name1.capitalize(), name2.capitalize(), name3.capitalize()


class StudentResource(Resource):
    @api_item(Student.select, 'admin')
    def put(self, student: Student):
        args = parser_full.parse_args()
        student.load_class(args['year'])
        old_class_n = student.class_n
        class_ = split_class(args['class'])
        name1, name2, name3 = parse_name(args['name1'], args['name2'], args['name3'])
        new = Student.build(None, name1, name2, name3, args['gender'], args['other_id'], allow_empty=True)
        class_n = class_[0] or student.class_n
        class_l = class_[1] or student.class_l
        school_id = args['school'] or student.school_id
        student ^= new
        if get_student_by_params(args['year'], name1, name2, class_n, class_l):
            return False, {'message': 'Такой участник уже есть'}
        if not School.select(school_id):
            return False, {'message': 'Такой школы нет'}
        student_id = student.id
        Student.update(student)
        sc = StudentClass.build(student_id, args['year'], class_n, class_l, school_id)
        if StudentClass.select(args['year'], student_id):
            StudentClass.update(sc)
        else:
            StudentClass.insert(sc)
        if old_class_n:
            Generator.gen_students_list(args['year'], old_class_n)
        if class_n:
            Generator.gen_students_list(args['year'], class_n)
        return True, {'message': 'Данные изменены'}

    @api_item(Student.select, 'admin')
    def delete(self, student: Student):
        Student.delete(student)
        StudentClass.delete_by_student(student.id)
        return True, {'message': 'Участник удалён'}


class StudentListResource(Resource):
    @api_group('admin')
    def post(self):
        args = parser_full.parse_args()
        class_n, class_l = split_class(args['class'])
        name1, name2, name3 = parse_name(args['name1'], args['name2'], args['name3'])
        school_id = args['school']
        student = Student.build(None, name1, name2, name3, args['gender'], args['other_id'])
        if get_student_by_params(args['year'], name1, name2, class_n, class_l):
            return False, {'message': 'Такой участник уже есть'}
        if not School.select(school_id):
            return False, {'message': 'Такой школы нет'}
        student_id = Student.insert(student, return_id=True)
        StudentClass.insert(StudentClass.build(student_id, args['year'], class_n, class_l, school_id))
        Generator.gen_students_list(args['year'], class_n)
        return True, {'message': 'Участник добавлен'}
