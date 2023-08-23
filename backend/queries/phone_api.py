from backend import app
from ..database import Barcode, Iti, Student, StudentClass, User
from .help import check_block_iti
from flask import render_template, send_file, request, jsonify
from flask_cors import cross_origin
'''
    /<iti_id>/student_info                  Возвращает информацию по ID школьника (admin).
    /<iti_id>/save_barcodes                 Сохраняет таблицу с штрих-кодами (admin).
'''


@app.route("/<int:iti_id>/student_info", methods=['POST'])
@cross_origin()
@check_block_iti()
def student_info(iti: Iti):
    try:
        student_id = request.json['student_id']
        user_login = request.json['user_login']
        user_password = request.json['user_password']
        user = User.select_by_login(user_login)
        if not user:
            raise ValueError("Неверные логин пользователя")
        if not user.check_password(user_password):
            raise ValueError("Неверные пароль пользователя")
        if not user.can_do(-1):
            raise ValueError("Пользователь не является администратором")
        student = Student.select(student_id)
        if not student:
            raise ValueError("Такого школника нет")
        student_class = StudentClass.select(iti.id, student_id)
        if not student_class:
            raise ValueError("Школник не участвует в этом ИТИ")
        return jsonify({'status': 'OK', 'student': student.json(), 'student_class': student_class.json()})
    except Exception as ex:
        return jsonify({'status': 'Error', 'msg': str(ex)})


@app.route("/<int:iti_id>/save_barcodes", methods=['POST'])
@cross_origin()
@check_block_iti()
def save_barcodes(iti: Iti):
    try:
        data = request.json['data']
        user_login = request.json['user_login']
        user_password = request.json['user_password']
        user = User.select_by_login(user_login)
        if not user:
            raise ValueError("Неверные логин пользователя")
        if not user.check_password(user_password):
            raise ValueError("Неверные пароль пользователя")
        if not user.can_do(-1):
            raise ValueError("Пользователь не является администратором")
        value = json.loads(data)
        for line in value:
            student_id = line[0]
            if not Student.select(student_id):
                raise ValueError('Школьника "{}" не существует'.format(student_id))
            for barcode in line[1:]:
                bar = Barcode.select(iti.id, barcode)
                if bar and bar.student_id != student_id:
                    raise ValueError('Штрих-код "{}" уже сохранён на школьника "{}"'.format(barcode, student_id))
        for line in value:
            student_id = line[0]
            for barcode in line[1:]:
                if not Barcode.select(iti.id, barcode):
                    Barcode.insert(Barcode.build(iti.id, barcode, student_id))
    except Exception as ex:
        return jsonify({'status': 'Error', 'msg': str(ex)})
    return jsonify({'status': 'OK'})
