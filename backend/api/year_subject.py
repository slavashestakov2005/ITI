from flask_login import current_user
from flask_restful import reqparse, Resource
from . import get_point
from ..api import api_item, api_group
from ..database import Subject, Year, YearSubject, YearSubjectScore
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
parser_full.add_argument('score_2', required=False, type=int)
parser_full.add_argument('score_3', required=False, type=int)
parser_full.add_argument('score_4', required=False, type=int)
parser_full.add_argument('score_5', required=False, type=int)
parser_full.add_argument('score_6', required=False, type=int)
parser_full.add_argument('score_7', required=False, type=int)
parser_full.add_argument('score_8', required=False, type=int)
parser_full.add_argument('score_9', required=False, type=int)


class YearSubjectResource(Resource):
    @api_item(YearSubject.select)
    def put(self, ys: YearSubject):
        args = parser_full.parse_args()
        year = Year.select(ys.year)
        if not year:
            return False, {'message': 'Этого года нет'}
        if not Subject.select(ys.subject):
            return False, {'message': 'Этого предмета нет'}

        if args['type'] == 'description':
            if not current_user.can_do(-1):
                return False, {'message': 'Доступ запрещён'}
            if args['n_d'] and args['n_d'] <= 0:
                return False, {'message': 'Отрицательный номер дня'}
            start = get_point(args['date'], args['start'])
            end = get_point(args['date'], args['end'])
            new = YearSubject.build(ys.id, ys.year, ys.subject, start, end, args['classes'], args['place'], args['n_d'],
                                    allow_empty=True)
            ys ^= new
            YearSubject.update(ys)
            Generator.gen_timetable(ys.year)
            Generator.gen_years_subjects_list(ys.year)
        elif args['type'] == 'score':
            if not current_user.can_do(ys.subject):
                return False, {'message': 'Доступ запрещён'}
            for cls in year.classes:
                score = args['score_' + cls]
                YearSubjectScore.update(YearSubjectScore.build(ys.id, int(cls), score))
        else:
            return False, {'message': 'Неизвестный тип запроса'}
        return True, {'message': 'Сохранено'}


class YearSubjectListResource(Resource):
    @api_group('admin')
    def post(self):
        args = parser_simple.parse_args()
        year, subjects = args['year'], args['subject']
        year = Year.select(year)
        if not year:
            return False, {'message': 'Этого года нет'}
        old_subjects = YearSubject.select_by_year(year.year)
        old_sub_sub = [x.subject for x in old_subjects]
        old_sub_id = [x.id for x in old_subjects]
        for i, x in enumerate(old_sub_sub):
            if x not in subjects:
                YearSubject.delete(year.year, x)
                YearSubjectScore.delete_by_year_subject(old_sub_id[i])
        for x in subjects:
            if x not in old_sub_sub:
                ys = YearSubject.insert(YearSubject.build(None, year.year, x, 0, 0, year.classes, '', 0, allow_empty=True), return_id=True)
                for cls in year.classes:
                    YearSubjectScore.insert(YearSubjectScore.build(ys, int(cls), year.default_score))
        FileCreator.create_subjects(year.year, subjects)
        Generator.gen_years_subjects_list(year.year)
        return True, {'message': 'Сохранено'}
