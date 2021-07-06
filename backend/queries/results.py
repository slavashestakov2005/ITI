from backend import app
from backend.help.errors import forbidden_error
from ..database import ResultsTable, Result, SubjectsTable
from flask import render_template, request
from flask_cors import cross_origin
from flask_login import login_required, current_user
from .help import check_status
from .auto_generator import Generator
'''
    tour_type(name)                                             Преобразует названия туров.
    /<path1>/<path2>/<path3>/add_result     add_result(...)     redirect на страницу редактирования (для предметников).
    /<path1>/<path2>/<path3>/save_result    save_result(...)    Сохранение результатов (для предметников).
    /<path1>/<path2>/<path3>/share_results  share_results(...)  Генерирует таблицу с результатами (admin).
'''


def tour_type(name: str) -> str:
    if name == 'individual':
        return 'Индивидуальный тур'
    elif name == 'group':
        return 'Групповой тур'
    return 'Командный тур'


@app.route('/<path:path1>/<path:path2>/<path:path3>/add_result')
@cross_origin()
@login_required
def add_result(path1, path2, path3):
    subject = int(path3[:-5])
    if not current_user.can_do(subject):
        return forbidden_error()
    print('Add result ', path1, path2, path3)
    return render_template('add_result.html', year=path1, subject=subject, h_type_1=path2, h_type_2=tour_type(path2),
                           h_sub_name=SubjectsTable.select_by_id(subject).name)


@app.route('/<path:path1>/<path:path2>/<path:path3>/save_result', methods=['POST'])
@cross_origin()
@login_required
def save_result(path1, path2, path3):
    year = int(path1)
    subject = int(path3[:-5])
    user_id = request.form['code']
    result = request.form['result']
    if not current_user.can_do(subject):
        return forbidden_error()
    r = Result([year, subject, user_id, result])
    if user_id == "" or result == "":
        return render_template('add_result.html', year=year, subject=subject, error1='Поля не заполнены', h_type_1=path2,
                               h_type_2=tour_type(path2),h_sub_name=SubjectsTable.select_by_id(subject).name)
    if not ResultsTable.select_for_people(r).__is_none__:
        if not current_user.can_do(-1):
            return render_template('add_result.html', year=year, subject=subject, h_type_1=path2, h_type_2=tour_type(path2),
                                   h_sub_name=SubjectsTable.select_by_id(subject).name,
                                   error1='Результат участника ' + str(user_id) + ' уже сохранён. Для изменения ' +
                                         'необходимы права администратора')
        else:
            ResultsTable.update(r)
    else:
        ResultsTable.insert(r)
    return render_template('add_result.html', year=year, subject=subject, h_type_1=path2, h_type_2=tour_type(path2),
                           h_sub_name=SubjectsTable.select_by_id(subject).name,
                           error1='Результат участника ' + str(user_id) + ' сохранён')


@app.route('/<path:path1>/<path:path2>/<path:path3>/share_results')
@cross_origin()
@login_required
@check_status('admin')
def share_results(path1, path2, path3):
    year = int(path1)
    subject = int(path3[:-5])
    Generator.gen_results(year, subject, path1 + '/' + path2 + '/' + path3)
    return render_template('add_result.html', year=year, subject=subject, error2='Результаты опубликованы',
                           h_type_1=path2, h_type_2=tour_type(path2), h_sub_name=SubjectsTable.select_by_id(subject).name)
