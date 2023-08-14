from backend import app
from ..help import forbidden_error
from ..excel import ExcelResultsReader
from ..database import GroupResult, Result, StudentClass, Subject, Team, Year, YearSubject, YearSubjectScore
from flask import render_template, request
from flask_cors import cross_origin
from flask_login import login_required, current_user
from .help import check_status, check_block_year, path_to_subject, compare
from .auto_generator import Generator
from ..config import Config
from .messages_help import message_results_public, message_ratings_public, message_all_ratings_public
'''
    tour_type(name)                                             Переводит названия туров.
    tour_name(type)                                             Делает длинные названия туров из коротких.
    page_params(path1, path2, path3)                            Возвращает параметры для страницы 'add_result.html'.
    group_page_params(path1, path2, path3)                      Возвращает параметры для '<year>/add_result.html'.
    chose_params(path1, path2, path3)                           Выбирает между page_params() и group_page_params().
    /<path1>/<path2>/<path3>/add_result     add_result(...)     redirect на страницу редактирования (для предметников).
    /<path1>/<path2>/<path3>/load_result    load_result(...)    Загружает результаты (для предметников).
    /<path1>/<path2>/<path3>/share_results  share_results(...)  Генерирует таблицу с результатами (admin).
    /<year>/ratings_update                  ratings_update(...) Обновляет рейтинги (admin).
    /<path1>/share_all_results                       <...>
    /<path1>/<path2>/<path3>/share_group_results     <...>      Генерирует таблицу с групповыми результатами (admin).
'''


def tour_type(name: str) -> str:
    if name == 'individual':
        return 'Индивидуальный тур'
    elif name == 'group':
        return 'Групповой тур'
    return 'Командный тур'


def tour_name(type: str) -> str:
    if type == 'i':
        return 'individual'
    elif type == 'g':
        return 'group'
    return 'team'


def page_params(year: int, path2, path3):
    params = {'year': abs(year), 'h_type_1': path2, 'h_type_2': tour_type(path2)}
    try:
        params['subject'] = subject = path_to_subject(path3)
        sub = YearSubject.select(year, subject)
        scores = YearSubjectScore.select_by_year_subject(sub.id)
        params.update({'h_sub_name': Subject.select(subject).name, 'scores': scores})
        results = Result.select_by_year_subject(sub.id)
        year_info = Year.select(year)
        sorted_results = {int(cls): [] for cls in year_info.classes}
        sorted_results['?'] = []
        top = {}
        for r in results:
            if r.student_id:
                sc = StudentClass.select(year, r.student_id)
                if sc:
                    sorted_results[sc.class_number].append(r)
                    continue
            sorted_results['?'].append(r)
        for cls in sorted_results:
            lst = sorted_results[cls]
            lst.sort(key=compare(lambda x: Result.sort_by_result(x), field=True))
            t, last_pos, last_result = [], 0, None
            for i in range(len(lst)):
                if last_result != lst[i].result:
                    last_pos, last_result = i + 1, lst[i].result
                # if last_pos > 3:
                #    break
                # на сайте захотели все результаты
                t.append([last_pos, lst[i].student_code, lst[i].result])
            top[cls] = t
        params['top'] = top
    except Exception:
        pass
    return params


def group_page_params(year: int, path3):
    res = {'year': abs(year)}
    try:
        res['subject'] = subject = path_to_subject(path3)
        res['h_sub_name'] = Subject.select(subject).name
        teams = Team.select_by_year(year)
        for team in teams:
            gr = GroupResult.select_by_team_and_subject(team.id, subject)
            if gr is None:
                gr.result = 0
            res['t' + str(team.id)] = gr.result
    except Exception:
        pass
    return res


def chose_params(p1: int, p2: str, p3: str):
    return group_page_params(p1, p3) if p2 == 'group' or p2 == 'team' else page_params(p1, p2, p3)


@app.route('/<year:year>/<path:path3>/add_result')
@cross_origin()
@login_required
@check_block_year()
def add_result(year: int, path3):
    try:
        subject = Subject.select(path_to_subject(path3))
        if subject is None:
            raise ValueError()
    except Exception:
        return forbidden_error()
    if not current_user.can_do(subject.id):
        return forbidden_error()

    path2 = tour_name(subject.type)
    params = chose_params(year, path2, path3)
    if path2 == 'group' or path2 == 'team':
        return render_template(str(year) + '/add_result.html', **params)
    return render_template('add_result.html', **params)


@app.route('/<year:year>/<path:path3>/load_result', methods=['POST'])
@cross_origin()
@login_required
@check_block_year()
def load_result(year: int, path3):
    path2 = 'individual'
    url = 'add_result.html'
    try:
        subject = path_to_subject(path3)
        file = request.files['file']
        parts = [x.lower() for x in file.filename.rsplit('.', 1)]
        filename = Config.DATA_FOLDER + '/load_' + str(year) + '_' + str(subject) + '.' + parts[1]
    except Exception:
        params = page_params(year, path2, path3)
        return render_template(url, **params, error6=['[ Некорректные данные ]'])

    file.save(filename)
    # FileManager.save(filename)
    txt = ExcelResultsReader(filename, year, subject).read(current_user)
    params = page_params(year, path2, path3)
    if txt:
        return render_template(url, **params, error6=txt)
    return render_template(url, **params, error6=['[ Сохранено ]'])


@app.route('/<year:year>/<path:path3>/class_split_results')
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def class_split_results(year: int, path3):
    path2 = 'individual'
    params = page_params(year, path2, path3)
    url = 'add_result.html'
    try:
        subject = path_to_subject(path3)
    except Exception:
        return render_template(url, **params, error4='Некорректные данные')

    ys = YearSubject.select(year, subject)
    if not ys:
        return render_template(url, **params, error4='Такого предмета нет в этом году.')
    try:
        Generator.get_results_0(year, ys.id)
    except ValueError as ex:
        return render_template(url, **params, error4=str(ex))
    return render_template(url, **params, error4='Школьники разделены по классам')


@app.route('/<year:year>/<path:path3>/share_results')
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def share_results(year: int, path3):
    path2 = 'individual'
    params = page_params(year, path2, path3)
    url = 'add_result.html'
    try:
        subject = path_to_subject(path3)
    except Exception:
        return render_template(url, **params, error3='Некорректные данные')

    if YearSubject.select(year, subject) is None:
        return render_template(url, **params, error3='Такого предмета нет в этом году.')
    try:
        Generator.gen_results(Year.select(year), subject, str(year) + '/' + path3)
    except ValueError as ex:
        return render_template(url, **params, error3=str(ex))
    message_results_public(year, subject)
    return render_template(url, **params, error3='Результаты опубликованы')


'''
# Можно объединить с публикацией результатов, так как:
# 1. Меньше запросов к БД.
# 2. Меньше нажимать кнопок.
# 3. Это логично (участники могут сделать это и руками).
'''


@app.route("/<year:year>/ratings_update")
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def ratings_update(year: int):
    if Year.select(year) is None:
        return render_template(str(year) + '/rating.html', error='Этого года нет', year=abs(year))
    Generator.gen_ratings(year)
    message_ratings_public(year)
    return render_template(str(year) + '/rating.html', error='Рейтинги обновлены', year=abs(year))


@app.route('/<year:year>/<path:path3>/share_group_results')
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def share_group_results(year: int, path3):
    params = group_page_params(year, path3)
    try:
        subject = path_to_subject(path3)
    except Exception:
        return render_template('/add_result.html', **params, error2='Некорректные данные')

    if YearSubject.select(year, subject) is None:
        return render_template('/add_result.html', **params, error2='Такого предмета нет в этом году.')
    Generator.gen_group_results(year, subject, str(year) + '/' + path3)
    message_results_public(year, subject)
    return render_template(str(year) + '/add_result.html', **params, error2='Результаты опубликованы')


@app.route('/<year:year>/share_all_results')
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def share_all_results(year: int):
    ys = YearSubject.select_by_year(year)
    params = {'year': abs(year)}
    url = str(year) + '/rating.html'
    errors = []
    subjects = []
    for now in ys:
        subject = Subject.select(now.subject)
        subjects.append(subject)
        try:
            suf = str(subject.id) + '.html'
            if subject.type == 'i':
                Generator.gen_results(Year.select(year), subject.id, str(year) + '/' + suf)
            else:
                Generator.gen_group_results(year, subject.id, str(year) + '/' + suf)
        except ValueError:
            errors.append(subject.name)
    Generator.gen_ratings(year)
    if errors:
        return render_template(url, **params, error=', '.join(errors) + ' имеют неправильные результаты.')
    else:
        message_all_ratings_public(year, subjects)
        return render_template(url, **params, error='Рейтинги обновлены')
