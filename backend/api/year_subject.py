from flask_login import current_user
from flask_restful import reqparse, Resource
from . import get_point
from ..api import api_item, api_group
from ..database import Subject, Year, YearSubject
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
        if args['type'] == 'description':
            if not current_user.can_do(-1):
                return False, {'message': 'Доступ запрещён'}
            if any(args['score_' + str(_)] for _ in range(2, 10)):
                return False, {'message': 'Переданы лишние аргументы запроса'}
        elif args['type'] == 'score':
            if not current_user.can_do(ys.subject):
                return False, {'message': 'Доступ запрещён'}
            if args['classes'] or args['place'] or args['n_d'] or args['date'] or args['start'] or args['end']:
                return False, {'message': 'Переданы лишние аргументы запроса'}
        else:
            return False, {'message': 'Неизвестный тип запроса'}
        if args['n_d'] and args['n_d'] <= 0:
            return False, {'message': 'Отрицательный номер дня'}
        start = get_point(args['date'], args['start'])
        end = get_point(args['date'], args['end'])
        if not Year.select(ys.year):
            return False, {'message': 'Этого года нет'}
        if not Subject.select(ys.subject):
            return False, {'message': 'Этого предмета нет'}
        new = YearSubject.build(ys.year, ys.subject, args['score_5'] or args['score_2'], args['score_6'] or args['score_3'],
                                args['score_7'] or args['score_4'], args['score_8'], args['score_9'], start, end,
                                args['classes'], args['place'], args['n_d'], allow_empty=True)
        ys ^= new
        YearSubject.update(ys)
        if args['type'] == 'description':
            Generator.gen_timetable(ys.year)
            Generator.gen_years_subjects_list(ys.year)
        return True, {'message': 'Сохранено'}


class YearSubjectListResource(Resource):
    @api_group('admin')
    def post(self):
        args = parser_simple.parse_args()
        year, subjects = args['year'], args['subject']
        print(subjects)
        print(year)
        if not Year.select(year):
            return False, {'message': 'Этого года нет'}
        old_sub = [x.subject for x in YearSubject.select_by_year(year)]
        for x in old_sub:
            if x not in subjects:
                YearSubject.delete(year, x)
        for x in subjects:
            if x not in old_sub:
                d = 30 if year > 0 else 0
                YearSubject.insert(YearSubject.build(year, x, 30, 30, 30, d, d, 0, 0, '', '', 0, allow_empty=True))
        FileCreator.create_subjects(year, subjects)
        Generator.gen_years_subjects_list(year)
        return True, {'message': 'Сохранено'}
