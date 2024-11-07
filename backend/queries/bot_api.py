from flask import jsonify, request
from flask_cors import cross_origin

from backend import app
from ..config import Config
from ..database import ItiSubject, Result, Student, StudentEljur, Subject, TgUser


def get_results_for_student(student: Student, year: int):
    data = []
    for r in Result.select_for_student(student.id):
        if r.position > 0:
            ys = ItiSubject.select_by_id(r.iti_subject_id)
            if ys.iti_id == year:
                data.append([Subject.select(ys.subject_id).name, r.position, r.result, r.net_score])
    return data


@app.route("/api/bot/get_student", methods=['POST'])
@cross_origin()
def get_student():
    try:
        api_key = request.json['api_key']
        tg_id = int(request.json['tg_id'])
        if api_key != Config.BOT_KEY:
            raise ValueError("Неверный ключ бота")
        tg_user = TgUser.select(tg_id)
        if tg_user is None:
            raise ValueError("Пользователь не найден")
        se = StudentEljur.select_by_eljur(tg_user.eljur_id)
        if se is None:
            raise ValueError("Не знаем Eljur пользователя")
        student = Student.select(se.student_id)
        if student is None:
            raise ValueError("Не нашли школьника")
        return jsonify({'status': 'OK', 'data': {'student': student.json(), 'role': tg_user.role}})
    except Exception as ex:
        return jsonify({'status': 'Error', 'msg': str(ex)})


@app.route("/api/bot/get_results", methods=['POST'])
@cross_origin()
def get_results():
    try:
        api_key = request.json['api_key']
        student_id = request.json['student_id']
        iti_id = request.json['iti_id']
        if api_key != Config.BOT_KEY:
            raise ValueError("Неверный ключ бота")
        student = Student.select(student_id)
        if not student:
            raise ValueError("Такого школьника нет")
        results = get_results_for_student(student, iti_id)
        return jsonify({'status': 'OK', 'results': results})
    except Exception as ex:
        return jsonify({'status': 'Error', 'msg': str(ex)})
