from backend import app
from ..database import Barcode, Iti, ItiSubject, Student, StudentClass, Subject, User
from .help import check_block_iti
from .results_raw import save_result_
from flask import request, jsonify
from flask_cors import cross_origin
import json
'''
    /<iti_id>/student_info                  Возвращает информацию по ID школьника (scaner).
    /<iti_id>/subject_info                  Возрващает информацию по ID предмета (scaner).
    /<iti_id>/save_barcodes                 Сохраняет таблицу с штрих-кодами (scaner).
    /<iti_id>/<subject_id>/save_results     Сохраняет результаты по предмету (предметник).
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
        if not user.can_do(-3):
            raise ValueError("Пользователь не является сканером")
        student = Student.select(student_id)
        if not student:
            raise ValueError("Такого школьника нет")
        student_class = StudentClass.select(iti.id, student_id)
        if not student_class:
            raise ValueError("Школьник не участвует в этом ИТИ")
        return jsonify({'status': 'OK', 'student': student.json(), 'student_class': student_class.json()})
    except Exception as ex:
        return jsonify({'status': 'Error', 'msg': str(ex)})


@app.route("/<int:iti_id>/subject_info", methods=['POST'])
@cross_origin()
@check_block_iti()
def subject_info(iti: Iti):
    try:
        subject_id = request.json['subject_id']
        user_login = request.json['user_login']
        user_password = request.json['user_password']
        user = User.select_by_login(user_login)
        if not user:
            raise ValueError("Неверные логин пользователя")
        if not user.check_password(user_password):
            raise ValueError("Неверные пароль пользователя")
        if not user.can_do(-3):
            raise ValueError("Пользователь не является сканером")
        subject = Subject.select(subject_id)
        if not subject:
            raise ValueError("Такого предмета нет")
        iti_subject = ItiSubject.select(iti.id, subject_id)
        if not iti_subject:
            raise ValueError("Этого предмета нет в этом ИТИ")
        return jsonify({'status': 'OK', 'subject': subject.json()})
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
        if not user.can_do(-3):
            raise ValueError("Пользователь не является сканером")
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


@app.route("/<int:iti_id>/<int:subject_id>/save_results", methods=['POST'])
@cross_origin()
@check_block_iti()
def save_subject_results(iti: Iti, subject_id: int):
    try:
        data = request.json['data']
        user_login = request.json['user_login']
        user_password = request.json['user_password']
        user = User.select_by_login(user_login)
        if not user:
            raise ValueError("Неверные логин пользователя")
        if not user.check_password(user_password):
            raise ValueError("Неверные пароль пользователя")
        if not user.can_do(subject_id):
            raise ValueError("Пользователь не может редактировать этот предмет")
        value = json.loads(data)
        ans = {}
        for i, line in enumerate(value):
            student_code, result = line
            answer = save_result_(user, iti.id, subject_id, int(student_code), str(result))
            if answer:
                if answer not in ans:
                    ans[answer] = []
                ans[answer].append(str(i + 1))
        decode = {-1: 'Вам запрещено редактирование',
                  0: 'Несуществующий шифр в строках: ' + (','.join(ans[0]) if 0 in ans else ''),
                  1: 'Пустые ячеёки в строках: ' + (','.join(ans[1]) if 1 in ans else ''),
                  3: ('Такого предмета нет в этом году',),
                  4: 'Повтор кодов в строках: ' + (','.join(ans[4]) if 4 in ans else ''),
                  5: 'Неправильный формат для результата в строках: ' + (','.join(ans[5]) if 5 in ans else ''),
                  6: 'Сумма баллов больше 30: ' + (','.join(ans[6]) if 6 in ans else ''),
                  7: 'Нет такого ИТИ',
                  8: 'По этому штрих-коду результат уже сохранён: ' + (','.join(ans[8]) if 8 in ans else '')}
        txt = [decode[key] for key in decode if key in ans]
        if len(txt):
            raise ValueError('\n'.join(txt))
    except Exception as ex:
        return jsonify({'status': 'Error', 'msg': str(ex)})
    return jsonify({'status': 'OK'})
