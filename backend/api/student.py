from flask_restful import reqparse, Resource
from ..api import api_item, api_group
from ..database import Student
from ..queries.auto_generator import Generator
from ..queries.help import split_class


parser_full = reqparse.RequestParser()
parser_full.add_argument('class', required=True, type=str)
parser_full.add_argument('name1', required=True, type=str)
parser_full.add_argument('name2', required=True, type=str)
parser_full.add_argument('gender', required=True, type=str)


class StudentResource(Resource):
    @api_item(Student.select, 'admin')
    def put(self, student: Student):
        args = parser_full.parse_args()
        class_ = split_class(args['class'])
        name1, name2 = args['name1'].capitalize(), args['name2'].capitalize()
        new = Student.build(None, name1, name2, class_[0], class_[1].capitalize(), args['gender'], allow_empty=True)
        old_class_n = student.class_n
        student ^= new
        if Student.select_by_student(student):
            return False, {'message': 'Такой участник уже есть'}
        Student.update(student)
        Generator.gen_students_list(old_class_n)
        Generator.gen_students_list(student.class_n)
        return True, {'message': 'Данные изменены'}

    @api_item(Student.select, 'admin')
    def delete(self, student: Student):
        Student.delete(student)
        return True, {'message': 'Участник удалён'}


class StudentListResource(Resource):
    @api_group('admin')
    def post(self):
        args = parser_full.parse_args()
        class_ = split_class(args['class'])
        name1, name2 = args['name1'].capitalize(), args['name2'].capitalize()
        student = Student.build(None, name1, name2, class_[0], class_[1].capitalize(), args['gender'])
        class_n = student.class_n
        if Student.select_by_student(student):
            return False, {'message': 'Такой участник уже есть'}
        Student.insert(student)
        Generator.gen_students_list(class_n)
        return True, {'message': 'Участник добавлен'}
