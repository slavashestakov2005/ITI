from flask_restful import reqparse, Resource
from ..api import api_item, api_group, str_or_int
from ..config import Config
from ..database import Year
from ..queries.auto_generator import Generator
from ..queries.file_creator import FileCreator
from ..queries.full import _delete_year
from ..queries.help import SplitFile


parser_simple = reqparse.RequestParser()
parser_simple.add_argument('year', required=True, type=int)
parser_simple.add_argument('classes', required=True, type=str)
parser_simple.add_argument('ind_days', required=True, type=str_or_int)
parser_simple.add_argument('default_score', required=True, type=str_or_int)
parser_simple.add_argument('teams', required=True, type=str_or_int)
parser_simple.add_argument('students_in_team', required=True, type=str_or_int)
parser_simple.add_argument('sum_individual', required=True, type=str_or_int)
parser_block = reqparse.RequestParser()
parser_block.add_argument('block', required=True, type=int)


class YearResource(Resource):
    @api_item(Year.select, 'full')
    def delete(self, year: Year):
        _delete_year(year.year)
        return True, {'message': 'Год удалён'}

    @api_item(Year.select, 'full')
    def put(self, year: Year):
        args = parser_block.parse_args()
        year.block = args['block']
        Year.update(year)
        data = SplitFile(Config.TEMPLATES_FOLDER + '/' + str(year.year) + '/year_block.html')
        data.insert_after_comment(' is_block ', '''
                    <p><input type="radio" name="block" value="0" {0}>Разблокировано</p>
                    <p><input type="radio" name="block" value="1" {1}>Заблокировано</p>
                '''.format('checked' if year.block == 0 else '', 'checked' if year.block == 1 else ''))
        data.save_file()
        return True, {'message': 'Статус блокировки сохранён'}


class YearListResource(Resource):
    @api_group('full')
    def post(self):
        args = parser_simple.parse_args()
        year = args['year']
        if abs(year) <= 2000 or abs(year) >= 2100:
            return False, {'message': 'Некорректный год'}
        if Year.select(year):
            return False, {'message': 'Год уже существует'}
        year_info = Year.build(None, year, args['classes'], args['ind_days'], args['default_score'], args['teams'],
                               args['students_in_team'], args['sum_individual'], 0)
        Year.insert(year_info)
        FileCreator.create_year(year)
        Generator.gen_years_lists()
        Generator.gen_years_subjects_list(year)
        return True, {'message': 'Год добавлен'}

    @api_group('full')
    def put(self):
        args = parser_simple.parse_args()
        year = Year.select(args['year'])
        if not year:
            return False, {'message': 'Года не существует'}
        new = Year.build(None, args['year'], args['classes'], args['ind_days'], args['default_score'], args['teams'],
                         args['students_in_team'], args['sum_individual'], 0, allow_empty=True)
        year ^= new
        Year.update(year)
        Generator.gen_years_lists()
        return True, {'message': 'Год изменён'}
