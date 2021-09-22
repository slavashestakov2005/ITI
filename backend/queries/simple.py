from backend import app
from flask import render_template, redirect
from flask_cors import cross_origin
from flask_login import current_user
from ..help.errors import forbidden_error, not_found_error
from .help import LOGIN_REQUIRED_FILES, STATUS_REQUIRED_FILES, current_year
from jinja2 import TemplateNotFound
import os
from ..config import Config
'''
    /           index()             Возвращает стартовую страницу.
    /<path>     static_file(path)   Возвращает статическую страницу, проверяя статус пользователя и доступ к файлу.
'''


@app.route('/')
@cross_origin()
def index():
    y = current_year()
    if os.path.exists(Config.TEMPLATES_FOLDER + '/' + str(y) + '/main.html'):
        return redirect(str(y) + '/main.html')
    else:
        return render_template('index.html')


@app.route('/<path:path>')
@cross_origin()
def static_file(path):
    parts = [x.lower() for x in path.rsplit('.', 1)]
    if path in LOGIN_REQUIRED_FILES and (not current_user.is_authenticated
                                         or path in STATUS_REQUIRED_FILES
                                         and current_user.status not in STATUS_REQUIRED_FILES[path]):
        return forbidden_error()
    try:
        if len(parts) >= 2 and parts[1] == 'html':
            parts = path.split('/')
            if parts[0].isdigit():
                return render_template(path, year=parts[0])
            else:
                return render_template(path)
        return app.send_static_file(path)
    except TemplateNotFound:
        return not_found_error()


# [[maybe_unused]]
@app.route('/bie')
@cross_origin()
def bie():
    raise ValueError("Goodbye!")
