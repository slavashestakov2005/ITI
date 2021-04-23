from flask import render_template
from flask_login import current_user
from functools import wraps
from glob import glob
from backend.config import Config


LOGIN_REQUIRED_FILES = []
STATUS_REQUIRED_FILES = {}


def create_forbidden_error():
    return render_template('403.html'), 403


def parse_files():
    if len(LOGIN_REQUIRED_FILES) > 0:
        return
    path = Config.TEMPLATES_FOLDER + "/"
    length = len(path)
    for file_name in glob(path + '**/*.html', recursive=True):
        with open(file_name, 'r', encoding='utf-8') as f:
            line1 = f.readline()
            line2 = f.readline()
        if line1 == "<!-- login required -->\n":
            LOGIN_REQUIRED_FILES.append(file_name[length:])
            begin = line2[0:5]
            end = line2[-5:-1]
            if begin == '<!-- ' and end == ' -->':
                value = int(line2[5:-5])
                if value > 0:
                    STATUS_REQUIRED_FILES[file_name[length:]] = {value, -2, -1}
                elif value == -1:
                    STATUS_REQUIRED_FILES[file_name[length:]] = {-2, -1}
                else:
                    STATUS_REQUIRED_FILES[file_name[length:]] = {-2}
    print("Login required files: " + str(LOGIN_REQUIRED_FILES))
    print("Status: " + str(STATUS_REQUIRED_FILES))


def check_status(status: str):
    def my_decorator(function_to_decorate):

        @wraps(function_to_decorate)
        def wrapped(*args, **kwargs):
            print('We are check current user')
            if status == 'admin':
                value = -1
            elif status == 'full':
                value = -2
            else:
                value = int(status)
            if not current_user.can_do(value):
                return create_forbidden_error()
            return function_to_decorate(*args, **kwargs)

        return wrapped

    return my_decorator

