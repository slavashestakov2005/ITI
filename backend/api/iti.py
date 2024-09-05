from flask_restful import reqparse, Resource

from ..api import api_group, api_item, ApiStatus, str_or_int
from ..database import Iti
from ..help import UserRoleGlobal, UserRoleIti
from ..queries.auto_generator import Generator
from ..queries.file_creator import FileCreator
from ..queries.full import _delete_iti


parser_simple = reqparse.RequestParser()
parser_simple.add_argument('name_in_list', required=True, type=str)
parser_simple.add_argument('name_on_page', required=True, type=str)
parser_simple.add_argument('classes', required=True, type=str)
parser_simple.add_argument('ind_days', required=True, type=str_or_int)
parser_simple.add_argument('default_ind_score', required=True, type=str_or_int)
parser_simple.add_argument('net_score_formula', required=True, type=str_or_int)
parser_simple.add_argument('ind_res_per_day', required=True, type=str_or_int)
parser_simple.add_argument('ind_prize_policy', required=True, type=str_or_int)
parser_simple.add_argument('automatic_division', required=True, type=str_or_int)
parser_simple.add_argument('auto_teams', required=True, type=str)
parser_simple.add_argument('sum_ind_to_team', required=True, type=str_or_int)
parser_simple.add_argument('sum_gr_to_ind_policy', required=True, type=str_or_int)
parser_simple.add_argument('sum_gr_to_super', required=True, type=str_or_int)
parser_simple.add_argument('super_open_policy', required=True, type=str_or_int)
parser_simple.add_argument('students_in_team', required=True, type=str_or_int)
parser_simple.add_argument('encoding_type', required=True, type=str_or_int)
parser_simple.add_argument('description', required=True, type=str)
parser_full = parser_simple.copy()
parser_full.add_argument('id', required=True, type=int)
parser_block = reqparse.RequestParser()
parser_block.add_argument('block', required=True, type=int)


class ItiResource(Resource):
    @api_item(db=Iti.select, roles=[UserRoleGlobal.CHANGE_ITI, UserRoleIti.ADMIN])
    def delete(self, iti: Iti):
        _delete_iti(iti.id)
        return ApiStatus.Ok, {'message': 'ИТИ удалены'}

    @api_item(db=Iti.select, roles=[UserRoleGlobal.CHANGE_ITI, UserRoleIti.ADMIN])
    def put(self, iti: Iti):
        args = parser_block.parse_args()
        iti.block = args['block']
        Iti.update(iti)
        Generator.gen_iti_block_page(iti)
        return ApiStatus.OK, {'message': 'Статус блокировки сохранён'}


class ItiListResource(Resource):
    @api_group(roles=[UserRoleGlobal.CHANGE_ITI])
    def post(self):
        args = parser_simple.parse_args()
        iti_info = Iti.build(None, args['name_in_list'], args['name_on_page'], args['classes'], args['ind_days'],
                             args['default_ind_score'], args['net_score_formula'], args['ind_res_per_day'],
                             args['ind_prize_policy'], args['automatic_division'], args['auto_teams'],
                             args['sum_ind_to_team'], args['sum_gr_to_ind_policy'], args['sum_gr_to_super'], args['super_open_policy'],
                             args['students_in_team'], args['encoding_type'], args['description'], 0)
        iti_id = Iti.insert(iti_info, return_id=True)
        FileCreator.create_iti(iti_id)
        Generator.gen_iti_lists()
        Generator.gen_iti_subjects_list(iti_id)
        return ApiStatus.OK, {'message': 'ИТИ добавлены'}

    @api_group(roles=[UserRoleGlobal.CHANGE_ITI])
    def put(self):
        args = parser_full.parse_args()
        iti_info = Iti.select(args['id'])
        if not iti_info:
            return ApiStatus.FAIL, {'message': 'ИТИ не существует'}
        new = Iti.build(None, args['name_in_list'], args['name_on_page'], args['classes'], args['ind_days'],
                        args['default_ind_score'], args['net_score_formula'], args['ind_res_per_day'],
                        args['ind_prize_policy'], args['automatic_division'], args['auto_teams'],
                        args['sum_ind_to_team'], args['sum_gr_to_ind_policy'], args['sum_gr_to_super'], args['super_open_policy'],
                        args['students_in_team'], args['encoding_type'], args['description'], None, allow_empty=True)
        iti_info ^= new
        Iti.update(iti_info)
        Generator.gen_iti_lists()
        return ApiStatus.OK, {'message': 'ИТИ изменены'}
