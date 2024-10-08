from flask_restful import reqparse, Resource

from ..api import api_group, api_item, ApiStatus
from ..database import Subject
from ..help import UserRoleGlobal
from ..queries.auto_generator import Generator
from ..queries.help import correct_new_line


parser_full = reqparse.RequestParser()
parser_full.add_argument('name', required=True, type=str)
parser_full.add_argument('short_name', required=True, type=str)
parser_full.add_argument('type', required=True, type=str)
parser_full.add_argument('diploma', required=True, type=str)
parser_full.add_argument('msg', required=True, type=str)


class SubjectResource(Resource):
    @api_item(db=Subject.select, roles=[UserRoleGlobal.CHANGE_SUBJECT])
    def put(self, subject: Subject):
        args = parser_full.parse_args()
        args['diploma'], args['msg'] = correct_new_line(args['diploma']), correct_new_line(args['msg'])
        if args['type'] and args['type'] not in ['i', 'g', 'a']:
            return ApiStatus.FAIL, {'message': 'Неверный тип предмета'}
        if Subject.select_by_name(args['name']) and args['name'] != subject.name:
            return ApiStatus.FAIL, {'message': 'Имя предмета занято'}
        new = Subject.build(None, args['name'], args['short_name'], args['type'], args['diploma'], args['msg'],
                            allow_empty=True)
        subject ^= new
        Subject.update(subject)
        Generator.gen_subjects_lists()
        return ApiStatus.OK, {'message': 'Предмет обновлён'}

    @api_item(db=Subject.select, roles=[UserRoleGlobal.CHANGE_SUBJECT])
    def delete(self, subject: Subject):
        Subject.delete(subject)
        Generator.gen_subjects_lists()
        return ApiStatus.OK, {'message': 'Предмет удалён'}


class SubjectListResource(Resource):
    @api_group(roles=[UserRoleGlobal.CHANGE_SUBJECT])
    def post(self):
        args = parser_full.parse_args()
        args['diploma'], args['msg'] = correct_new_line(args['diploma']), correct_new_line(args['msg'])
        if args['type'] not in ['i', 'g', 'a']:
            return ApiStatus.FAIL, {'message': 'Неверный тип предмета'}
        if Subject.select_by_name(args['name']):
            return ApiStatus.FAIL, {'message': 'Имя предмета занято'}
        subject = Subject.build(None, args['name'], args['short_name'], args['type'], args['diploma'], args['msg'])
        type, name = subject.type, subject.name
        Subject.insert(subject)
        subject = Subject.select_by_name(name)
        Generator.gen_subjects_lists()
        if type == 'g':
            Generator.gen_rules(subject)
        return ApiStatus.OK, {'message': 'Предмет добавлен' +
                                         (', не забудьте добавить его правила и ссылку на них' if type == 'g' else '')}
