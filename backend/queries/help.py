from flask import render_template
from functools import wraps
from glob import glob
from jinja2 import Environment, FileSystemLoader
import re

from backend.config import Config
from backend.help.errors import forbidden_error
from ..database import Iti
from ..help import check_role, jinja_context, krsk_time

'''
    correct_new_line(str)           Заменяет все переносы строк на '\n'.
    split_class(str)                Разбивает класс на букву и цифру.
    empty_checker(*args)            Проверяет аргументы на пустую строку и выбрасывает ValueError.
    @check_access(status, block)    Проверяет открыт ли доступ для текущего пользователя.
'''


def correct_new_line(s: str):
    return re.sub(r'[\n\r]+', r'\n', s)


def split_class(class_):
    class_ = str(class_)
    if len(class_) == 0:
        return ['', '']
    if len(class_) == 1:
        return int(class_), ''
    return int(class_[:-1]), class_[-1].capitalize()


def empty_checker(*args):
    for x in args:
        if not x or not len(x):
            raise ValueError


def check_access(*, roles: list=None, block: bool=None):
    def my_decorator(function_to_decorate):

        @wraps(function_to_decorate)
        def wrapped(*args, **kwargs):
            try:
                iti_id = kwargs['iti_id']
            except Exception:
                if not check_role(roles=roles):
                    return forbidden_error()
                return function_to_decorate(*args, **kwargs)
            if not check_role(roles=roles, iti_id=iti_id):
                return forbidden_error()
            iti_info = Iti.select(iti_id)
            kwargs['iti'] = iti_info
            kwargs.pop('iti_id', None)
            if not iti_info or block and iti_info.block:
                return forbidden_error()
            
            return function_to_decorate(*args, **kwargs)

        return wrapped

    return my_decorator


def route_iti_html_page(*, page: str, roles=None, block: bool=None, root: bool=False):
    def my_decorator(function_to_decorate):

        @wraps(function_to_decorate)
        def wrapped(iti_id: int):
            try:
                if not check_role(roles=roles, iti_id=iti_id):
                    raise ValueError()
                iti = Iti.select(iti_id)
                if not iti or block and iti.block:
                    raise ValueError()
                params = function_to_decorate(iti)
            except Exception:
                return forbidden_error()
            template = page if root else '{}/{}.html'.format(iti.id, page)
            return render_template(template, iti=iti, **params)

        return wrapped

    return my_decorator


def set_filter(seq):
    return set(seq)


def html_render(template_name: str, output_name: str, template_folder: str = Config.HTML_FOLDER,
                output_folder: str = Config.TEMPLATES_FOLDER, **data):
    env = Environment(loader=FileSystemLoader(template_folder))
    env.filters['set'] = set_filter
    template = env.get_template(template_name)
    for key, val in jinja_context().items():
        data[key] = val
    data['krsk_moment'] = krsk_time
    data = template.render(**data)
    data += '\n' if data[-1] != '\n' else ''
    with open(output_folder + '/' + output_name, 'w', encoding='UTF-8') as f:
        f.write(data)
