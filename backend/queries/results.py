from backend import app
from backend.help.errors import forbidden_error
from ..database import ResultsTable, Result, SubjectsTable, YearsSubjectsTable, TeamsTable,\
    GroupResultsTable, GroupResult, AppealsTable, Appeal, StudentsCodesTable, StudentsTable
from flask import render_template, request
from flask_cors import cross_origin
from flask_login import login_required, current_user
from .help import check_status
from .auto_generator import Generator
import re
'''
    tour_type(name)                                             Преобразует названия туров.
    page_params(path1, path2, path3)                            Возвращает параметры для страницы 'add_result.html'.
    appeal_page_params(path1, path2, path3)                     Возвращает пераметры для страницы 'add_appeal.html'
    group_page_params(path1, path2, path3)                      Возвращает параметры для '<year>/add_result.html'.
    /<path1>/<path2>/<path3>/add_result     add_result(...)     redirect на страницу редактирования (для предметников).
    /<path1>/<path2>/<path3>/save_result    save_result(...)    Сохранение результатов (для предметников).
    /<path1>/<path2>/<path3>/share_results  share_results(...)  Генерирует таблицу с результатами (admin).
    /<year>/ratings_update                  ratings_update(...) Обновляет рейтинги (admin).
    /<path1>/<path2>/<path3>/save_group_results      <...>      Сохранение групповых результатов (для предметников).
    /<path1>/<path2>/<path3>/share_group_results     <...>      Генерирует таблицу с групповыми результатами (admin).
    /<path1>/<path2>/<path3>/add_appeal     add_appeal(...)     Сохранение апелляций и redirect на эту страницу.
'''


def tour_type(name: str) -> str:
    if name == 'individual':
        return 'Индивидуальный тур'
    elif name == 'group':
        return 'Групповой тур'
    return 'Командный тур'


def page_params(path1, path2, path3):
    subject = int(path3[:-5])
    sub = YearsSubjectsTable.select(int(path1), subject)
    appeals = AppealsTable.select_by_year_and_subject(int(path1), subject)
    appeals = [(_, StudentsTable.select(
        StudentsCodesTable.select_by_code(int(path1), _.student).student
    )) for _ in appeals]
    return {'year': path1, 'subject': subject, 'h_type_1': path2, 'h_type_2': tour_type(path2),
             'h_sub_name': SubjectsTable.select_by_id(subject).name, 's5': sub.score_5, 's6': sub.score_6,
            's7': sub.score_5, 's8': sub.score_8, 's9': sub.score_9, 'appeals': appeals}


def appeal_page_params(path1, path2, path3):
    subject = int(path3[:-5])
    return {'year': path1, 'subject': subject, 'h_type_1': path2, 'h_type_2': tour_type(path2),
            'h_sub_name': SubjectsTable.select_by_id(subject).name}


def group_page_params(path1, path2, path3):
    subject = int(path3[:-5])
    res = {'year': path1, 'subject': subject, 'h_type_1': path2, 'h_type_2': tour_type(path2),
           'h_sub_name': SubjectsTable.select_by_id(subject).name}
    teams = TeamsTable.select_by_year(int(path1))
    for team in teams:
        gr = GroupResultsTable.select_by_team_and_subject(team.id, subject)
        if gr.__is_none__:
            gr.result = 0
        res['t' + str(team.id)] = gr.result
    return res


@app.route('/<path:path1>/<path:path2>/<path:path3>/add_result')
@cross_origin()
@login_required
def add_result(path1, path2, path3):
    subject = int(path3[:-5])
    if not current_user.can_do(subject):
        return forbidden_error()
    print('Add result ', path1, path2, path3)
    if path2 == 'group' or path2 == 'team':
        return render_template(path1 + '/add_result.html', **group_page_params(path1, path2, path3))
    return render_template('add_result.html', **page_params(path1, path2, path3))


@app.route('/<path:path1>/<path:path2>/<path:path3>/save_result', methods=['POST'])
@cross_origin()
@login_required
def save_result(path1, path2, path3):
    year = int(path1)
    subject = int(path3[:-5])
    user_id = request.form['code']
    result_sum = sum(map(int, re.split('\D+', request.form['result'])))
    text_result = ' '.join(re.split('[^\dXxХх]+', request.form['result']))
    if not current_user.can_do(subject):
        return forbidden_error()
    r = Result([year, subject, user_id, result_sum, 0, text_result])
    if user_id == "" or request.form['result'] == "":
        return render_template('add_result.html', **page_params(path1, path2, path3), error2='Поля не заполнены')
    if not ResultsTable.select_for_people(r).__is_none__:
        if not current_user.can_do(-1):
            return render_template('add_result.html', **page_params(path1, path2, path3),
                                   error2='Результат участника ' + str(user_id) + ' уже сохранён. Для изменения ' +
                                         'необходимы права администратора')
        else:
            ResultsTable.update(r)
    else:
        ResultsTable.insert(r)
    return render_template('add_result.html', **page_params(path1, path2, path3),
                           error2='Результат участника ' + str(user_id) + ' сохранён')


@app.route('/<path:path1>/<path:path2>/<path:path3>/share_results')
@cross_origin()
@login_required
@check_status('admin')
def share_results(path1, path2, path3):
    year = int(path1)
    subject = int(path3[:-5])
    try:
        Generator.gen_results(year, subject, path1 + '/' + path2 + '/' + path3)
    except ValueError:
        return render_template('add_result.html', **page_params(path1, path2, path3),
                error3='Сохранены некоректные результаты (есть участник с количеством баллов большим максимального)')
    return render_template('add_result.html', **page_params(path1, path2, path3), error3='Результаты опубликованы')


'''
# Можно объединить с публикацией результатов, так как:
# 1. Меньше запросов к БД.
# 2. Меньше нажимать кнопок.
# 3. Это логично (участники могут сделать это и руками).
'''


@app.route("/<path:year>/ratings_update")
@cross_origin()
@login_required
@check_status('admin')
def ratings_update(year):
    year = int(year)
    Generator.gen_ratings(year)
    return render_template(str(year) + '/rating.html', error='Рейтинги обновлены', year=year)


@app.route('/<path:path1>/<path:path2>/<path:path3>/save_group_results', methods=['POST'])
@cross_origin()
@login_required
def save_group_results(path1, path2, path3):
    year = int(path1)
    subject = int(path3[:-5])
    if not current_user.can_do(subject):
        return forbidden_error()
    teams = TeamsTable.select_by_year(year)
    for team in teams:
        gr = GroupResult([team.id, subject, int(request.form['score_' + str(team.id)])])
        if GroupResultsTable.select_by_team_and_subject(team.id, subject).__is_none__:
            GroupResultsTable.insert(gr)
        else:
            GroupResultsTable.update(gr)
    return render_template(str(year) + '/add_result.html', **group_page_params(path1, path2, path3),
                           error1='Результаты сохранены')


@app.route('/<path:path1>/<path:path2>/<path:path3>/share_group_results')
@cross_origin()
@login_required
@check_status('admin')
def share_group_results(path1, path2, path3):
    year = int(path1)
    subject = int(path3[:-5])
    Generator.gen_group_results(year, subject, path1 + '/' + path2 + '/' + path3)
    return render_template(str(year) + '/add_result.html', **group_page_params(path1, path2, path3),
                           error2='Результаты опубликованы')


@app.route('/<path:path1>/<path:path2>/<path:path3>/add_appeal', methods=['GET', 'POST'])
@cross_origin()
@login_required
def add_appeal(path1, path2, path3):
    params = appeal_page_params(path1, path2, path3)
    if request.method == 'POST':
        year = int(path1)
        subject = int(path3[:-5])
        code = int(request.form['code'])
        tasks = request.form['tasks']
        description = request.form['description']
        AppealsTable.insert(Appeal([year, subject, code, tasks, description]))
        params['error1'] = 'Апелляция подана'
    return render_template('add_appeal.html', **params)
