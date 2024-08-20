from flask_restful import reqparse, Resource

from ..api import api_item
from ..database import Barcode, Iti


parser_simple = reqparse.RequestParser()
parser_simple.add_argument('barcode', required=True, type=int)
parser_simple.add_argument('student_id', required=True, type=int)


class BarcodeListResource(Resource):
    @api_item(Iti.select, 'admin')
    def post(self, iti: Iti):
        args = parser_simple.parse_args()
        barcode, student = args['barcode'], args['student_id']
        old_bar = Barcode.select(iti.id, barcode)
        editing = (old_bar.student_id != student) if old_bar else False
        if old_bar:
            Barcode.delete(old_bar)
        Barcode.insert(Barcode.build(iti.id, barcode, student))
        if editing:
            return True, {'message': 'Данные по штрих-коду отредактированы'}
        return True, {'message': 'Данные по штрих-коду сохранены'}

    @api_item(Iti.select, 'admin')
    def delete(self, iti: Iti):
        args = parser_simple.parse_args()
        barcode, student = args['barcode'], args['student_id']
        old_bar = Barcode.select(iti.id, barcode)
        if not old_bar:
            return True, {'message': 'Такого штрих-кода и не было'}
        Barcode.delete(old_bar)
        return True, {'message': 'Данные по штрих-коду удалены'}
