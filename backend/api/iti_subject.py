from flask_restful import reqparse, Resource

from . import get_point
from ..api import api_group, api_item, ApiStatus
from ..database import Iti, ItiSubject, ItiSubjectScore, Subject
from ..help import check_role, UserRoleIti, UserRoleItiSubject
from ..queries.auto_generator import Generator
from ..queries.file_creator import FileCreator


parser_simple = reqparse.RequestParser()
parser_simple.add_argument('year', required=True, type=int)
parser_simple.add_argument('subject', required=False, type=int, action='append', default=list)
parser_full = reqparse.RequestParser()
parser_full.add_argument('type', required=True, type=str)
parser_full.add_argument('classes', required=False, type=str)
parser_full.add_argument('place', required=False, type=str)
parser_full.add_argument('n_d', required=False, type=int)
parser_full.add_argument('date', required=False, type=str)
parser_full.add_argument('start', required=False, type=str)
parser_full.add_argument('end', required=False, type=str)
parser_full.add_argument('timezone', required=False, type=int)
parser_full.add_argument('score_2', required=False, type=int)
parser_full.add_argument('score_3', required=False, type=int)
parser_full.add_argument('score_4', required=False, type=int)
parser_full.add_argument('score_5', required=False, type=int)
parser_full.add_argument('score_6', required=False, type=int)
parser_full.add_argument('score_7', required=False, type=int)
parser_full.add_argument('score_8', required=False, type=int)
parser_full.add_argument('score_9', required=False, type=int)


class ItiSubjectResource(Resource):
    @api_item(db=ItiSubject.select)
    def put(self, iti_subjects: ItiSubject):
        args = parser_full.parse_args()
        iti_info = Iti.select(iti_subjects.iti_id)
        if not iti_info:
            return ApiStatus.FAIL, {'message': 'Этого ИТИ нет'}
        if not Subject.select(iti_subjects.subject_id):
            return ApiStatus.FAIL, {'message': 'Этого предмета нет'}

        if args['type'] == 'description':
            if not check_role(roles=[UserRoleIti.ADMIN], iti_id=iti_info.id):
                return ApiStatus.ACCESS_DENIED, {}
            if args['n_d'] and args['n_d'] <= 0:
                return ApiStatus.FAIL, {'message': 'Отрицательный номер дня'}
            start = get_point(args['date'], args['start'], args['timezone'])
            end = get_point(args['date'], args['end'], args['timezone'])
            new = ItiSubject.build(iti_subjects.id, iti_subjects.iti_id, iti_subjects.subject_id, start, end,
                                   args['classes'], args['place'], args['n_d'], allow_empty=True)
            iti_subjects ^= new
            ItiSubject.update(iti_subjects)
            Generator.gen_timetable(iti_subjects.iti_id)
            Generator.gen_iti_subjects_list(iti_subjects.iti_id)
        elif args['type'] == 'score':
            if not check_role(roles=[UserRoleItiSubject.EDIT_SCORE], iti_id=iti_info.id, iti_subject_id=iti_subjects.id):
                return ApiStatus.ACCESS_DENIED, {}
            for cls in iti_info.classes_list():
                score = args['score_{}'.format(cls)]
                ItiSubjectScore.update(ItiSubjectScore.build(iti_subjects.id, cls, score))
        else:
            return ApiStatus.FAIL, {'message': 'Неизвестный тип запроса'}
        return ApiStatus.OK, {'message': 'Сохранено'}


class ItiSubjectListResource(Resource):
    @api_group()
    def post(self):
        args = parser_simple.parse_args()
        year, subjects = args['year'], args['subject']
        if not check_role(roles=[UserRoleIti.ADMIN], iti_id=year):
            return ApiStatus.ACCESS_DENIED, {}
        iti_info = Iti.select(year)
        if not iti_info:
            return ApiStatus.FAIL, {'message': 'Этого года нет'}
        old_subjects = ItiSubject.select_by_iti(iti_info.id)
        old_sub_sub = [x.subject_id for x in old_subjects]
        old_sub_id = [x.id for x in old_subjects]
        for i, x in enumerate(old_sub_sub):
            if x not in subjects:
                ItiSubject.delete(iti_info.id, x)
                ItiSubjectScore.delete_by_iti_subject(old_sub_id[i])
        for x in subjects:
            if x not in old_sub_sub:
                iti_subject_id = ItiSubject.insert(ItiSubject.build(None, iti_info.id, x, 0, 0, iti_info.classes, '', 0,
                                                                    allow_empty=True), return_id=True)
                for cls in iti_info.classes_list():
                    ItiSubjectScore.insert(ItiSubjectScore.build(iti_subject_id, cls, iti_info.default_ind_score))
        FileCreator.create_subjects(iti_info, subjects)
        Generator.gen_iti_subjects_list(iti_info.id)
        return ApiStatus.OK, {'message': 'Сохранено'}
