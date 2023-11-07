from flask import make_response, jsonify
from flask_cors import cross_origin
from flask_login import current_user
from functools import wraps
from ..help import EmptyFieldException, get_timestamp


def check_status(status):
    if status is None:
        return True
    if status == 'login':
        return current_user.is_authenticated
    if status == 'admin':
        value = -1
    elif status == 'full':
        value = -2
    else:
        value = int(status)
    return current_user.can_do(value)


def api_item(method, status=None):
    def my_decorator(function_to_decorate):

        @wraps(function_to_decorate)
        @cross_origin()
        def wrapped(_, *args, **kwargs):
            try:
                if not check_status(status):
                    return make_response(jsonify({'status': 'FAIL', 'message': 'Доступ запрещён'}), 403)
                value = method(*args, *kwargs.values())
                if value is None:
                    return make_response(jsonify({'status': 'FAIL', 'message': 'ID не существует'}), 404)
                result, data = function_to_decorate(_, value)
                data['status'] = 'OK' if result else 'FAIL'
                return make_response(jsonify(data), 200 if result else 404)
            except EmptyFieldException as ex:
                return make_response(jsonify({'status': 'FAIL', 'message': 'Пустое поле ' + str(ex)}), 404)
            except Exception as ex:
                return make_response(jsonify({'status': 'FAIL', 'message': 'Ошибка на сервере ' + str(ex)}), 500)

        return wrapped

    return my_decorator


def api_group(status=None):
    def my_decorator(function_to_decorate):

        @wraps(function_to_decorate)
        @cross_origin()
        def wrapped(_):
            try:
                if not check_status(status):
                    return make_response(jsonify({'status': 'FAIL', 'message': 'Доступ запрещён'}), 403)
                result, data = function_to_decorate(_)
                data['status'] = 'OK' if result else 'FAIL'
                return make_response(jsonify(data), 200 if result else 404)
            except EmptyFieldException as ex:
                return make_response(jsonify({'status': 'FAIL', 'message': 'Пустое поле ' + str(ex)}), 404)
            except Exception as ex:
                return make_response(jsonify({'status': 'FAIL', 'message': 'Ошибка на сервере ' + str(ex)}), 500)

        return wrapped

    return my_decorator


def get_point(date: str, time: str, timezone_minutes: int, null=True):
    if not date or not time:
        return None if null else get_timestamp()
    date = [int(_) for _ in date.split('-')]
    time = [int(_) for _ in time.split(':')]
    return get_timestamp(*date, *time) + timezone_minutes * 60


def str_or_int(value):
    if value == '':
        return ''
    elif type(value) == str and value.isdigit() or type(value) == int:
        return int(value)
    else:
        raise ValueError("Cannot parse argument {} as empty string or digit".format(value))
