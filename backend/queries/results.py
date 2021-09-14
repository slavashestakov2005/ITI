from backend import app
from backend.help.errors import forbidden_error
from ..database import ResultsTable, Result, SubjectsTable, YearsSubjectsTable, TeamsTable,\
    GroupResultsTable, GroupResult, AppealsTable, Appeal, StudentsCodesTable, StudentsTable, YearsTable
from flask import render_template, request
from flask_cors import cross_origin
from flask_login import login_required, current_user
from .help import check_status, check_block_year, correct_new_line, path_to_subject
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


def page_params(year: int, path2, path3):
    params = {'year': year, 'h_type_1': path2, 'h_type_2': tour_type(path2)}
    try:
        params['subject'] = subject = path_to_subject(path3)
        sub = YearsSubjectsTable.select(year, subject)
        appeals = AppealsTable.select_by_year_and_subject(year, subject)
        appeals = [(_, StudentsTable.select(
            StudentsCodesTable.select_by_code(year, _.student).student
        )) for _ in appeals]
        params.update({'h_sub_name': SubjectsTable.select_by_id(subject).name, 's5': sub.score_5, 's6': sub.score_6,
            's7': sub.score_7, 's8': sub.score_8, 's9': sub.score_9, 'appeals': appeals})
    except Exception:
        pass
    return params


def appeal_page_params(year: int, path2, path3):
    params = {'year': year, 'h_type_1': path2, 'h_type_2': tour_type(path2)}
    try:
        params['subject'] = subject = path_to_subject(path3)
        params['h_sub_name'] = SubjectsTable.select_by_id(subject).name
    except Exception:
        pass
    return params


def group_page_params(year: int, path2, path3):
    res = {'year': year, 'h_type_1': path2, 'h_type_2': tour_type(path2)}
    try:
        res['subject'] = subject = path_to_subject(path3)
        res['h_sub_name'] = SubjectsTable.select_by_id(subject).name
        teams = TeamsTable.select_by_year(year)
        for team in teams:
            gr = GroupResultsTable.select_by_team_and_subject(team.id, subject)
            if gr.__is_none__:
                gr.result = 0
            res['t' + str(team.id)] = gr.result
    except Exception:
        pass
    return res


def chose_params(p1: int, p2: str, p3: str):
    return group_page_params(p1, p2, p3) if p2 == 'group' or p2 == 'team' else page_params(p1, p2, p3)


@app.route('/<int:year>/<path:path2>/<path:path3>/add_result')
@cross_origin()
@login_required
@check_block_year()
def add_result(year: int, path2, path3):
    params = chose_params(year, path2, path3)
    try:
        subject = path_to_subject(path3)
    except Exception:
        return forbidden_error()

    if not current_user.can_do(subject):
        return forbidden_error()
    if path2 == 'group' or path2 == 'team':
        return render_template(str(year) + '/add_result.html', **params)
    return render_template('add_result.html', **params)


@app.route('/<int:year>/<path:path2>/<path:path3>/save_result', methods=['POST'])
@cross_origin()
@login_required
@check_block_year()
def save_result(year: int, path2, path3):
    params = page_params(year, path2, path3)
    try:
        subject = path_to_subject(path3)
        user_id = int(request.form['code'])
        res = request.form['result'].replace(',', '.')
        result_sum = sum(map(float, re.split(r'[^\d\.]+', res)))
        text_result = re.sub('[XxХх]', 'X', ' '.join(re.split(r'[^\dXxХх\.]+', res)))
    except Exception:
        return render_template('add_result.html', **params, error2='Некорректные данные')

    if not current_user.can_do(subject):
        return forbidden_error()
    r = Result([year, subject, user_id, result_sum, 0, text_result])
    if user_id == "" or request.form['result'] == "":
        return render_template('add_result.html', **params, error2='Поля не заполнены')
    if StudentsCodesTable.select_by_code(year, user_id).__is_none__:
        return render_template('add_result.html', **params, error2='Такого кода нет')
    if YearsSubjectsTable.select(year, subject).__is_none__:
        return render_template('add_result.html', **params, error2='Такого предмета нет в этом году.')
    if not ResultsTable.select_for_people(r).__is_none__:
        if not current_user.can_do(-1):
            return render_template('add_result.html', **params, error2='Результат участника {0} уже сохранён. Для '
                                        'изменения необходимы права администратора'.format(user_id))
        else:
            ResultsTable.update(r)
    else:
        ResultsTable.insert(r)
    return render_template('add_result.html', **params, error2='Результат участника {0} сохранён'.format(user_id))


@app.route('/<int:year>/<path:path2>/<path:path3>/share_results')
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def share_results(year: int, path2, path3):
    params = page_params(year, path2, path3)
    try:
        subject = path_to_subject(path3)
    except Exception:
        return render_template('add_result.html', **params, error3='Некорректные данные')

    if YearsSubjectsTable.select(year, subject).__is_none__:
        return render_template('add_result.html', **params, error3='Такого предмета нет в этом году.')
    try:
        Generator.gen_results(year, subject, str(year) + '/' + path2 + '/' + path3)
    except ValueError:
        return render_template('add_result.html', **params, error3='Сохранены некоректные результаты (есть участник с '
                                                                   'количеством баллов большим максимального)')
    return render_template('add_result.html', **params, error3='Результаты опубликованы')


'''
# Можно объединить с публикацией результатов, так как:
# 1. Меньше запросов к БД.
# 2. Меньше нажимать кнопок.
# 3. Это логично (участники могут сделать это и руками).
'''


@app.route("/<int:year>/ratings_update")
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def ratings_update(year: int):
    if YearsTable.select_by_year(year).__is_none__:
        return render_template(str(year) + '/rating.html', error='Этого года нет', year=year)
    Generator.gen_ratings(year)
    return render_template(str(year) + '/rating.html', error='Рейтинги обновлены', year=year)


@app.route('/<int:year>/<path:path2>/<path:path3>/save_group_results', methods=['POST'])
@cross_origin()
@login_required
@check_block_year()
def save_group_results(year: int, path2, path3):
    params = group_page_params(year, path2, path3)
    try:
        subject = path_to_subject(path3)
    except Exception:
        return render_template('/add_result.html', **params, error1='Некорректные данные')

    if not current_user.can_do(subject):
        return forbidden_error()
    if YearsSubjectsTable.select(year, subject).__is_none__:
        return render_template('/add_result.html', **params, error1='Такого предмета нет в этом году.')
    teams = TeamsTable.select_by_year(year)
    for team in teams:
        try:
            gr = GroupResult([team.id, subject, int(request.form['score_' + str(team.id)])])
        except Exception:
            return render_template('/add_result.html', **params, error1='Некорректные данные')

        if GroupResultsTable.select_by_team_and_subject(team.id, subject).__is_none__:
            GroupResultsTable.insert(gr)
        else:
            GroupResultsTable.update(gr)
    return render_template(str(year) + '/add_result.html', **params, error1='Результаты сохранены')


@app.route('/<int:year>/<path:path2>/<path:path3>/share_group_results')
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def share_group_results(year: int, path2, path3):
    params = group_page_params(year, path2, path3)
    try:
        subject = path_to_subject(path3)
    except Exception:
        return render_template('/add_result.html', **params, error2='Некорректные данные')

    if YearsSubjectsTable.select(year, subject).__is_none__:
        return render_template('/add_result.html', **params, error2='Такого предмета нет в этом году.')
    Generator.gen_group_results(year, subject, str(year) + '/' + path2 + '/' + path3)
    return render_template(str(year) + '/add_result.html', **params, error2='Результаты опубликованы')


@app.route('/<int:year>/<path:path2>/<path:path3>/add_appeal', methods=['GET', 'POST'])
@cross_origin()
@login_required
@check_block_year()
def add_appeal(year: int, path2, path3):
    params = appeal_page_params(year, path2, path3)
    try:
        subject = path_to_subject(path3)
    except Exception:
        return render_template('add_appeal.html', **params, error1='Некорректные данные')

    if YearsSubjectsTable.select(year, subject).__is_none__:
        return render_template('add_appeal.html', **params, error1='Такого предмета нет в этом году.')
    if request.method == 'POST':
        try:
            code = int(request.form['code'])
            tasks = request.form['tasks']
            description = correct_new_line(request.form['description'])
        except Exception:
            params['error1'] = 'Некорректные данные'
        else:
            if StudentsCodesTable.select_by_code(year, code).__is_none__:
                params['error1'] = 'Некорректный код'
            else:
                AppealsTable.insert(Appeal([year, subject, code, tasks, description]))
                params['error1'] = 'Апелляция подана'
    return render_template('add_appeal.html', **params)
