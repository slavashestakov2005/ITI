from flask_login import current_user
from functools import wraps
from glob import glob
from jinja2 import Environment, FileSystemLoader
import re

from backend.config import Config
from backend.help.errors import forbidden_error
from ..database import Iti
from ..help import correct_slash, krsk_time

'''
    LOGIN_REQUIRED_FILES = []       Файлы, доступные после входа на сайт.
    STATUS_REQUIRED_FILES = {}      Отображение файла и доступа к нему.
    all_templates()                 Список всех файлов-шаблонов из папки шаблонов.
    correct_new_line(str)           Заменяет все переносы строк на '\n'.
    split_class(str)                Разбивает класс на букву и цифру.
    empty_checker(*args)            Проверяет аргументы на пустую строку и выбрасывает ValueError.
    path_to_subject(path)           Извлекает id предмета из имени файла.
    parse_files()                   Проходит все файлы, генерирует списки доступа.
    @check_access(status, block)    Проверяет открыт ли доступ для текущего пользователя.
'''

LOGIN_REQUIRED_FILES = []
STATUS_REQUIRED_FILES = {}


def all_templates():
    return glob(Config.TEMPLATES_FOLDER + '/**/*.html', recursive=True)


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


def path_to_subject(path: str) -> int:
    return int(path.rsplit('.', 1)[0])


def parse_files():
    if len(LOGIN_REQUIRED_FILES) > 0:
        return
    path = Config.TEMPLATES_FOLDER + "/"
    length = len(path)
    for file_name in all_templates():
        with open(file_name, 'r', encoding='utf-8') as f:
            line1 = f.readline()
            line2 = f.readline()
        if line1 == "<!-- login required -->\n":
            LOGIN_REQUIRED_FILES.append(correct_slash(file_name[length:]))
            begin = line2[0:5]
            end = line2[-5:-1]
            if begin == '<!-- ' and end == ' -->':
                value = int(line2[5:-5])
                if value > 0:
                    STATUS_REQUIRED_FILES[correct_slash(file_name[length:])] = {value, -2, -1}
                elif value == -1:
                    STATUS_REQUIRED_FILES[correct_slash(file_name[length:])] = {-2, -1}
                else:
                    STATUS_REQUIRED_FILES[correct_slash(file_name[length:])] = {-2}
    print("Login required files: " + str(LOGIN_REQUIRED_FILES))
    print("Status: " + str(STATUS_REQUIRED_FILES))


def check_access(status: str=None, block: bool=None):
    def my_decorator(function_to_decorate):

        @wraps(function_to_decorate)
        def wrapped(*args, **kwargs):
            if status is not None:
                if status == 'admin':
                    value = -1
                elif status == 'full':
                    value = -2
                else:
                    value = int(status)
                if not current_user.can_do(value):
                    return forbidden_error()
            
            try:
                iti_id = kwargs['iti_id']
            except Exception:
                return function_to_decorate(*args, **kwargs)
            iti_info = Iti.select(iti_id)
            kwargs['iti'] = iti_info
            kwargs.pop('iti_id', None)
            if not iti_info or block and iti_info.block:
                return forbidden_error()
            
            return function_to_decorate(*args, **kwargs)

        return wrapped

    return my_decorator


default_replace = [['<!-- replace 1 -->', '{% extends "base.html" %}{% block content %}'],
                   ['<!-- replace 2 -->', '{% endblock %}\n']]


def set_filter(seq):
    return set(seq)


def html_render(template_name: str, output_name: str, template_folder: str = Config.HTML_FOLDER,
                output_folder: str = Config.TEMPLATES_FOLDER, replaced: list = None, **data):
    if replaced is None:
        replaced = []
    env = Environment(loader=FileSystemLoader(template_folder))
    env.filters['set'] = set_filter
    template = env.get_template(template_name)
    data['krsk_moment'] = krsk_time
    data = template.render(**data)
    for rep in default_replace:
        data = data.replace(rep[0], rep[1])
    for rep in replaced:
        data = data.replace(rep[0], rep[1])
    with open(output_folder + '/' + output_name, 'w', encoding='UTF-8') as f:
        f.write(data)
