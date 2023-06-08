from flask_restful import reqparse, Resource
from ..api import api_item, api_group
from ..config import Config
from ..database import Year
from ..queries.auto_generator import Generator
from ..queries.file_creator import FileCreator
from ..queries.full import _delete_year
from ..queries.help import SplitFile


parser_simple = reqparse.RequestParser()
parser_simple.add_argument('year', required=True, type=int)
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
        data = SplitFile(Config.TEMPLATES_FOLDER + '/' + str(year.year) + '/subjects_for_year.html')
        data.insert_after_comment(' is_block ', '''
                    <p><input type="radio" name="is_block" value="0" {0}>Разблокировано</p>
                    <p><input type="radio" name="is_block" value="1" {1}>Заблокировано</p>
                '''.format('checked' if year.block == 0 else '', 'checked' if year.block == 1 else ''))
        data.save_file()
        return True, {'message': 'Статус блокировки сохранён'}


class YearListResource(Resource):
    @api_group('full')
    def post(self):
        args = parser_simple.parse_args()
        value = args['year']
        if abs(value) <= 2000 or abs(value) >= 2100:
            return False, {'message': 'Некорректный год'}
        if Year.select(value):
            return False, {'message': 'Год уже существует'}
        year = Year.build(value, 0)
        Year.insert(year)
        FileCreator.create_year(value)
        Generator.gen_years_lists()
        Generator.gen_years_subjects_list(value)
        return True, {'message': 'Год добавлен'}
