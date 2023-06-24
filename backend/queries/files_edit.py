from backend import app
from flask import request, redirect, render_template, url_for
from flask_cors import cross_origin
from flask_login import login_required, current_user
from backend.config import Config
from .help import check_status, check_block_year, correct_new_line, path_to_subject, empty_checker
from ..help import not_found_error, forbidden_error, FileManager
from ..database import Student, StudentCode, Subject, Year, YearSubject
from .results import chose_params
from .auto_generator import Generator
import os
'''
    generate_filename...(...)               Генерирует имя для нового файла.
    /upload         upload()                Загружает файлы (admin).
    /<path>/edit    edit(path)              redirect на страницу с редактированием (admin).
    /editor         editor()                Возвращает html-код редактируемойстраницы (admin | full).
    /save_file      save_file()             Сохраняет изменения html-страницы (admin | full).
'''


def generate_filename(last_name, new_path, new_name):
    parts = [x.lower() for x in last_name.rsplit('.', 1)]
    if len(parts) < 2 or parts[1] not in Config.ALLOWED_EXTENSIONS:
        return None
    filename = os.path.join(os.path.realpath('.'), Config.UPLOAD_FOLDER, new_path)
    if not os.path.exists(filename):
        os.makedirs(filename)
    return new_path + '/' + new_name + '.' + parts[1]


def generate_filename_by_type(year: int, subject: int, types: list, classes: list):
    filename = 'ИТИ ' + str(abs(year)) + '. '
    subject = Subject.select(subject)
    if subject is None or not types or not classes or not len(types) or not len(classes):
        return None
    filename += subject.name + '. '
    types_translate = {'task': 'задания', 'solution': 'решения', 'criteria': 'критерии'}
    types = [types_translate[_] for _ in types]
    filename += types[0].title()
    for i in range(1, len(types)):
        filename += ' и ' if i == len(types) - 1 else ', '
        filename += types[i]
    filename += ' ' + classes[0]
    for i in range(1, len(classes)):
        filename += ', ' + classes[i]
    filename += ' классы' if len(classes) > 1 else ' класс'
    return filename


def generate_filename_by_student(year: int, subject: int, code: int, desc: str):
    filename = 'ИТИ ' + str(year) + '. '
    subject = Subject.select(subject)
    if subject is None:
        return None
    student = StudentCode.select_by_code(year, code, subject.n_d)
    if student is None:
        return None
    student = Student.select(student.student)
    if student is None:
        return None
    filename += subject.name + '. {} {} {}. '.format(student.name_1, student.name_2, student.class_name()) + desc
    return filename


@app.route("/upload", methods=['GET', 'POST'])
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def upload():
    if request.method == 'POST':
        try:
            file = request.files['file']
            new_path = request.form['new_path']
            new_name = request.form['new_name']
            empty_checker(new_name)
        except Exception:
            return forbidden_error()

        filename = generate_filename(file.filename, new_path, new_name)
        if filename:
            name = os.path.join(Config.UPLOAD_FOLDER, filename)
            file.save(name)
            FileManager.save(name)
            return redirect(filename)
    return render_template('upload.html')


@app.route('/<path:path>/edit')
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def edit(path):
    return redirect(url_for('editor', file_name=path))


@app.route('/editor')
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def editor():
    try:
        file_name = request.args.get('file_name')
        year = int(file_name.split('/')[0])
        y = Year.select(year)
        if y is None or y.block:
            return forbidden_error()
    except ValueError:
        pass
    except Exception:
        return forbidden_error()

    if file_name.count('/') == 0 and not current_user.can_do(-2):
        return forbidden_error()
    try:
        with open(Config.TEMPLATES_FOLDER + '/' + file_name, 'r', encoding='UTF-8') as f:
            file_text = f.read()
    except FileNotFoundError:
        return not_found_error()
    return render_template('file_edit.html', file_text=file_text, file_name=file_name)


@app.route('/save_file', methods=['POST'])
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def save_file():
    try:
        file_name = request.form['file_name']
    except Exception:
        return render_template('file_edit.html', file_text='', file_name='', error="Некорректное имя файла")
    try:
        file_text = correct_new_line(request.form['file_text'])
    except Exception:
        return render_template('file_edit.html', file_text='', file_name=file_name, error="Некорректное содержимое")

    if file_name.count('/') == 0 and not current_user.can_do(-2):
        return forbidden_error()
    name = Config.TEMPLATES_FOLDER + '/' + file_name
    with open(name, 'w', encoding='UTF-8') as f:
        f.write(file_text)
    FileManager.save(name)
    return render_template('file_edit.html', file_text=file_text, file_name=file_name, error="Файл сохранён")
