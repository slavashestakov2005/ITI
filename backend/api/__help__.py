from enum import Enum
from flask import jsonify, make_response
from flask_cors import cross_origin
from functools import wraps

from ..help import check_role, EmptyFieldException, get_timestamp


class ApiStatus(Enum):
    OK = 0
    ACCESS_DENIED = 1
    FAIL = 2


def api_item(*, db, roles=None):
    def my_decorator(function_to_decorate):

        @wraps(function_to_decorate)
        @cross_origin()
        def wrapped(_, *args, **kwargs):
            try:
                value = db(*args, *kwargs.values())
                if not check_role(roles=roles, iti_id=value.id if hasattr(value, 'id') else None):
                    return make_response(jsonify({'status': 'FAIL', 'message': 'Доступ запрещён'}), 403)
                if value is None:
                    return make_response(jsonify({'status': 'FAIL', 'message': 'ID не существует'}), 404)
                status, data = function_to_decorate(_, value)
                if status == ApiStatus.ACCESS_DENIED:
                    return make_response(jsonify({'status': 'FAIL', 'message': 'Доступ запрещён'}), 403)
                data['status'] = 'OK' if status == ApiStatus.OK else 'FAIL'
                return make_response(jsonify(data), 200 if status == ApiStatus.OK else 404)
            except EmptyFieldException as ex:
                return make_response(jsonify({'status': 'FAIL', 'message': 'Пустое поле ' + str(ex)}), 404)
            except Exception as ex:
                return make_response(jsonify({'status': 'FAIL', 'message': 'Ошибка на сервере ' + str(ex)}), 500)

        return wrapped

    return my_decorator


def api_group(*, roles=None):
    def my_decorator(function_to_decorate):

        @wraps(function_to_decorate)
        @cross_origin()
        def wrapped(_):
            try:
                if not check_role(roles=roles):
                    return make_response(jsonify({'status': 'FAIL', 'message': 'Доступ запрещён'}), 403)
                status, data = function_to_decorate(_)
                if status == ApiStatus.ACCESS_DENIED:
                    return make_response(jsonify({'status': 'FAIL', 'message': 'Доступ запрещён'}), 403)
                data['status'] = 'OK' if status == ApiStatus.OK else 'FAIL'
                return make_response(jsonify(data), 200 if status == ApiStatus.OK else 404)
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
