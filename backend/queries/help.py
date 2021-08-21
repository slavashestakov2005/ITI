from backend.help.errors import forbidden_error
from flask_login import current_user
from functools import wraps
from glob import glob
from backend.config import Config
import re
import os
'''
    LOGIN_REQUIRED_FILES = []       Файлы, доступные после входа на сайт.
    STATUS_REQUIRED_FILES = {}      Отображение файла и доступа к нему.
    all_templates()                 Список всех файлов-шаблонов из папки шаблонов.
    correct_slash(str)              Заменяет все слэши на '/'.
    split_class(str)                Разбивает класс на букву и цифру.
    parse_files()                   Проходит все файлы, генерирует списки доступа.
    @check_status(status)           Проверяет открыт ли доступ для текущего пользователя.
    class FilePart                  Один кусочек html-страницы (поля 'text' и 'is_comment').
    class SplitFile                 Связывает html-страницу и программное представление.
        __init__(file_name)                                 Парсит файл 'file_name'.
        insert_after_comment(comment, text, is_comment)     Добавляет 'text' после комментария 'comment'.
        replace_comment(comment, text)                      Заменяет комментарий 'comment' на 'text'.
        writable()                                          Генерирует строку для записи в файл.
        save_file(file_name)                                Сохраняет файл под именем 'file_name'.
'''

LOGIN_REQUIRED_FILES = []
STATUS_REQUIRED_FILES = {}


def all_templates():
    return glob(Config.TEMPLATES_FOLDER + '/**/*.html', recursive=True)


def correct_slash(s: str):
    return s.replace(r'\\', '/').replace('\\', '/').replace(r'//', '/')


def split_class(class_):
    return int(class_[:-1]), class_[-1],


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


def check_status(status: str):
    def my_decorator(function_to_decorate):

        @wraps(function_to_decorate)
        def wrapped(*args, **kwargs):
            if status == 'admin':
                value = -1
            elif status == 'full':
                value = -2
            else:
                value = int(status)
            if not current_user.can_do(value):
                return forbidden_error()
            return function_to_decorate(*args, **kwargs)

        return wrapped

    return my_decorator


class FilePart:
    def __init__(self, text, is_comment=False):
        self.text = text
        self.is_comment = is_comment


class SplitFile:
    def read_file(self):
        with open(self.file_name, 'r', encoding='UTF-8') as f:
            data = f.read()
        return re.split(r'(<!--|-->)', data)

    def __init__(self, file_name: str):
        self.file_name = file_name
        self.parts = []
        self.replace = {}
        self.edited = False
        is_comment = False
        parts = self.read_file()
        for part in parts:
            if part == '<!--':
                is_comment = True
            elif part == '-->':
                is_comment = False
            else:
                self.parts.append(FilePart(part, is_comment))

    def insert_after_comment(self, comment: str, text: str, is_comment: bool = False, append: bool = False):
        for index in range(len(self.parts)):
            if self.parts[index].is_comment and self.parts[index].text == comment:
                self.edited = True
                if not self.parts[index + 1].is_comment:
                    if not append:
                        self.parts[index + 1] = FilePart(text, is_comment)
                    else:
                        self.parts[index + 1] = FilePart(self.parts[index + 1].text + text, is_comment)
                else:
                    self.parts.insert(index + 1, FilePart(text))

    def replace_comment(self, comment: str, text: str):
        for index in range(len(self.parts)):
            if self.parts[index].is_comment and self.parts[index].text == comment:
                self.edited = True
                self.replace[index] = text

    def writable(self) -> str:
        result = ''
        index = 0
        for part in self.parts:
            if index in self.replace:
                result += self.replace[index]
            else:
                if part.is_comment:
                    result += '<!--'
                result += part.text
                if part.is_comment:
                    result += '-->'
            index += 1
        return result

    def save_file(self, file_name=None):
        if not file_name:
            file_name = self.file_name
        if self.edited:
            if not os.path.exists(os.path.dirname(file_name)):
                os.makedirs(os.path.dirname(file_name))
            with open(file_name, 'w', encoding='UTF-8') as f:
                f.write(self.writable())
        self.replace = {}
