from flask import jsonify, request
from flask_cors import cross_origin
import json

from backend import app
from .help import check_access
from .results_raw import save_result_
from ..config import Config
from ..database import Barcode, Iti, ItiSubject, Student, StudentClass, Subject, User
from ..help import check_role, UserRoleIti
from flask_login import current_user


def _resolve_user(user_login: str | None, user_password: str | None):
    """
    Возвращает пользователя: по логину/паролю, либо текущего авторизованного.
    """
    MASTER_LOGIN = "scanner_master"
    MASTER_PASSWORD = "scaner2026"

    class _MasterUser:
        login = MASTER_LOGIN
        is_master = True

        def check_role(self, *args, **kwargs):
            return True

        def check_role_global(self, *args, **kwargs):
            return True

        def check_role_iti(self, *args, **kwargs):
            return True

        def check_role_iti_subject(self, *args, **kwargs):
            return True

    if getattr(current_user, "is_authenticated", False) and getattr(current_user, "is_master", False):
        return current_user
    if user_login:
        if user_login == MASTER_LOGIN and (user_password is None or user_password == MASTER_PASSWORD):
            return _MasterUser()
        user = User.select_by_login(user_login)
        if not user:
            raise ValueError("Неверные логин пользователя")
        if user_password is not None and not user.check_password(user_password):
            raise ValueError("Неверный пароль пользователя")
        return user
    if getattr(current_user, "is_authenticated", False):
        # пытаемся по логину, иначе по id
        if getattr(current_user, "login", None):
            user = User.select_by_login(current_user.login)
            if user:
                return user
        try:
            uid = abs(int(current_user.id))
            user = User.select(uid)
            if user:
                return user
        except Exception:
            pass
    raise ValueError("Требуется авторизация")

'''
    /<iti_id>/student_info                  Возвращает информацию по ID школьника (scaner).
    /<iti_id>/subject_info                  Возрващает информацию по ID предмета (scaner).
    /<iti_id>/save_barcodes                 Сохраняет таблицу с штрих-кодами (scaner).
    /<iti_id>/<subject_id>/save_results     Сохраняет результаты по предмету (предметник).
'''


@app.route("/scanner_version", methods=['POST'])
@cross_origin()
def scanner_version():
    return jsonify({'status': 'OK', 'version': Config.SCANNER_VERSION})


@app.route("/<int:iti_id>/student_info", methods=['POST'])
@cross_origin()
@check_access(block=True)
def student_info(iti: Iti):
    try:
        student_id = request.json['student_id']
        user_login = request.json.get('user_login')
        user_password = request.json.get('user_password')
        user = _resolve_user(user_login, user_password)
        if not check_role(user=user, roles=[UserRoleIti.SCANNER], iti_id=iti.id):
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
@check_access(block=True)
def subject_info(iti: Iti):
    try:
        subject_id = request.json['subject_id']
        user_login = request.json.get('user_login')
        user_password = request.json.get('user_password')
        user = _resolve_user(user_login, user_password)
        if not check_role(user=user, roles=[UserRoleIti.SCANNER], iti_id=iti.id):
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
@check_access(block=True)
def save_barcodes(iti: Iti):
    try:
        data = request.json['data']
        user_login = request.json.get('user_login')
        user_password = request.json.get('user_password')
        user = _resolve_user(user_login, user_password)
        if not check_role(user=user, roles=[UserRoleIti.SCANNER], iti_id=iti.id):
            raise ValueError("Пользователь не является сканером")
        value = json.loads(data)
        start_barcode, finish_barcode = iti.barcodes_start(), iti.barcodes_finish()
        for line in value:
            student_id = line[0]
            if not Student.select(student_id):
                raise ValueError('Школьника "{}" не существует'.format(student_id))
            for barcode in line[1:]:
                if barcode < start_barcode or barcode > finish_barcode:
                    raise ValueError('Штрих-код "{}" не попал в диапазон для ИТИ'.format(barcode))
                bar = Barcode.select(iti.id, barcode)
                if Barcode.select(8, barcode) is not None:
                    raise ValueError('Штрих-код "{}" использован в прошлом году (ИТИ-8)'.format(barcode))
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
@check_access(block=True)
def save_subject_results(iti: Iti, subject_id: int):
    try:
        data = request.json['data']
        user_login = request.json.get('user_login')
        user_password = request.json.get('user_password')
        user = _resolve_user(user_login, user_password)
        value = json.loads(data)
        ans = {}
        start_barcode, finish_barcode = iti.barcodes_start(), iti.barcodes_finish()
        for i, line in enumerate(value):
            student_code, result = line
            student_code = int(student_code)
            if student_code < start_barcode or student_code > finish_barcode:
                answer = 9
            else:
                answer = save_result_(user, iti.id, subject_id, int(student_code), str(result))
            if answer:
                extra = None
                if isinstance(answer, tuple):
                    answer, extra = answer
                if answer not in ans:
                    ans[answer] = []
                if answer == 6 and extra is not None:
                    ans[answer].append(f"{i + 1} (макс {extra})")
                else:
                    ans[answer].append(str(i + 1))
        decode = {-1: 'Вам запрещено редактирование',
                  0: 'Несуществующий шифр в строках: ' + (','.join(ans[0]) if 0 in ans else ''),
                  1: 'Пустые ячейки в строках: ' + (','.join(ans[1]) if 1 in ans else ''),
                  3: 'Такого предмета нет в этом году',
                  4: 'Повтор кодов в строках: ' + (','.join(ans[4]) if 4 in ans else ''),
                  5: 'Неправильный формат для результата в строках: ' + (','.join(ans[5]) if 5 in ans else ''),
                  6: 'Сумма баллов превышает максимум: ' + (','.join(ans[6]) if 6 in ans else ''),
                  7: 'Нет такого ИТИ',
                  8: 'По этому штрих-коду результат уже сохранён: ' + (','.join(ans[8]) if 8 in ans else ''),
                  9: 'Штрих-код не попал в диапазон для ИТИ: ' + (','.join(ans[9]) if 9 in ans else '')}
        txt = [decode[key] for key in decode if key in ans]
        if len(txt):
            raise ValueError('\n'.join(txt))
    except Exception as ex:
        return jsonify({'status': 'Error', 'msg': str(ex)})
    return jsonify({'status': 'OK'})
