from backend import app
from ..help import forbidden_error
from ..database import GroupResult, Result, StudentClass, Subject, Team, Iti, ItiSubject, ItiSubjectScore
from flask import render_template, request
from flask_cors import cross_origin
from flask_login import login_required, current_user
from .help import check_status, check_block_iti, path_to_subject, compare
from .auto_generator import Generator
from .messages_help import message_results_public, message_ratings_public, message_all_ratings_public
'''
    /<iti_id>/<path>/add_result             redirect на страницу редактирования (для предметников).
    /<iti_id>/<path>/class_split_results    Разбивает индивидуальные результаты по параллелям (admin).
    /<iti_id>/<path>/share_results          Генерирует таблицу с индивидуальными результатами (admin).
    /<iti_id>/ratings_update                Обновляет рейтинги (admin).
    /<iti_id>/<path>/share_group_results    Генерирует таблицу с групповыми результатами (admin).
    /<iti_id>/share_all_results             Обновляет таблицы по всем предметам (admin).
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
        sub = ItiSubject.select(year, subject)
        scores = ItiSubjectScore.select_by_iti_subject(sub.id)
        params.update({'h_sub_name': Subject.select(subject).name, 'scores': scores})
        results = Result.select_by_iti_subject(sub.id)
        year_info = Iti.select(year)
        sorted_results = {cls: [] for cls in year_info.classes_list()}
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
        teams = Team.select_by_iti(year)
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


@app.route('/<int:iti_id>/<path:path3>/add_result')
@cross_origin()
@login_required
@check_block_iti()
def add_result(iti: Iti, path3):
    try:
        subject = Subject.select(path_to_subject(path3))
        if subject is None:
            raise ValueError()
    except Exception:
        return forbidden_error()
    if not current_user.can_do(subject.id):
        return forbidden_error()

    path2 = tour_name(subject.type)
    params = chose_params(iti.id, path2, path3)
    if path2 == 'group' or path2 == 'team':
        return render_template(str(iti.id) + '/add_result.html', **params)
    return render_template('add_result.html', **params)


@app.route('/<int:iti_id>/<path:path3>/class_split_results')
@cross_origin()
@login_required
@check_status('admin')
@check_block_iti()
def class_split_results(iti: Iti, path3):
    path2 = 'individual'
    params = page_params(iti.id, path2, path3)
    url = 'add_result.html'
    try:
        subject = path_to_subject(path3)
    except Exception:
        return render_template(url, **params, error4='Некорректные данные')

    ys = ItiSubject.select(iti.id, subject)
    if not ys:
        return render_template(url, **params, error4='Такого предмета нет в этом году.')
    try:
        Generator.get_results_0(iti, ys.id)
    except ValueError as ex:
        return render_template(url, **params, error4=str(ex))
    return render_template(url, **params, error4='Школьники разделены по классам')


@app.route('/<int:iti_id>/<path:path3>/share_results')
@cross_origin()
@login_required
@check_status('admin')
@check_block_iti()
def share_results(iti: Iti, path3):
    path2 = 'individual'
    params = page_params(iti.id, path2, path3)
    url = 'add_result.html'
    try:
        subject = path_to_subject(path3)
    except Exception:
        return render_template(url, **params, error3='Некорректные данные')

    if ItiSubject.select(iti.id, subject) is None:
        return render_template(url, **params, error3='Такого предмета нет в этом году.')
    try:
        Generator.gen_results(Iti.select(iti.id), subject, str(iti.id) + '/' + path3)
    except ValueError as ex:
        return render_template(url, **params, error3=str(ex))
    message_results_public(iti.id, subject)
    return render_template(url, **params, error3='Результаты опубликованы')


@app.route("/<int:iti_id>/ratings_update")
@cross_origin()
@login_required
@check_status('admin')
@check_block_iti()
def ratings_update(iti: Iti):
    Generator.gen_ratings(iti)
    message_ratings_public(iti.id)
    return render_template(str(iti.id) + '/rating.html', error='Рейтинги обновлены')


@app.route('/<int:iti_id>/<path:path3>/share_group_results')
@cross_origin()
@login_required
@check_status('admin')
@check_block_iti()
def share_group_results(iti: Iti, path3):
    params = group_page_params(iti.id, path3)
    try:
        subject = path_to_subject(path3)
    except Exception:
        return render_template('/add_result.html', **params, error2='Некорректные данные')

    if ItiSubject.select(iti.id, subject) is None:
        return render_template('/add_result.html', **params, error2='Такого предмета нет в этом году.')
    Generator.gen_group_results(iti.id, subject, str(iti.id) + '/' + path3)
    message_results_public(iti.id, subject)
    return render_template(str(iti.id) + '/add_result.html', **params, error2='Результаты опубликованы')


@app.route('/<int:iti_id>/share_all_results')
@cross_origin()
@login_required
@check_status('admin')
@check_block_iti()
def share_all_results(iti: Iti):
    ys = ItiSubject.select_by_iti(iti.id)
    params = {}
    url = str(iti.id) + '/rating.html'
    errors = []
    subjects = []
    for now in ys:
        subject = Subject.select(now.subject_id)
        subjects.append(subject)
        try:
            suf = str(subject.id) + '.html'
            if subject.type == 'i':
                Generator.gen_results(iti, subject.id, str(iti.id) + '/' + suf)
            else:
                Generator.gen_group_results(iti.id, subject.id, str(iti.id) + '/' + suf)
        except ValueError:
            errors.append(subject.name)
    Generator.gen_ratings(iti)
    if errors:
        return render_template(url, **params, error=', '.join(errors) + ' имеют неправильные результаты.')
    else:
        message_all_ratings_public(iti.id, subjects)
        return render_template(url, **params, error='Рейтинги обновлены')
