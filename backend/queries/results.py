from flask import render_template
from flask_cors import cross_origin
from flask_login import login_required

from backend import app
from .auto_generator import Generator
from .help import check_access
from .messages_help import message_all_ratings_public, message_ratings_public, message_results_public
from ..database import GroupResult, Iti, ItiSubject, ItiSubjectScore, Result, StudentClass, Subject, Team
from ..help import check_role, forbidden_error, UserRoleIti, UserRoleItiSubject

'''
    /<iti_id>/<subject_id>/add_result             Возвращает страницу редактирования по предмету (предметник).
    /<iti_id>/<subject_id>/class_split_results    Разделяет индивидуальные результаты по параллелям (admin).
    /<iti_id>/<subject_id>/share_results          Генерирует таблицу с индивидуальными результатами (admin).
    /<iti_id>/ratings_update                      Обновляет рейтинги (admin).
    /<iti_id>/<subject_id>/share_group_results    Генерирует таблицу с групповыми результатами (admin).
    /<iti_id>/share_all_results                   Обновляет таблицы по всем предметам (admin).
'''


def individual_page_params(iti: Iti, subject: Subject):
    params = {'iti': iti, 'year': iti.id, 'subject': subject.id, 'h_sub_name': subject.name}
    try:
        sub = ItiSubject.select(iti.id, subject.id)
        scores = ItiSubjectScore.select_by_iti_subject(sub.id)
        params['scores'] = scores
        results = Result.select_by_iti_subject(sub.id)
        sorted_results = {cls: [] for cls in iti.classes_list()}
        sorted_results['?'] = []
        top = {}
        for r in results:
            if r.student_id:
                sc = StudentClass.select(iti.id, r.student_id)
                if sc:
                    sorted_results[sc.class_number].append(r)
                    continue
            sorted_results['?'].append(r)
        for cls in sorted_results:
            lst = sorted_results[cls]
            lst.sort(key=Result.sort_by_result)
            t, last_pos, last_result = [], 0, None
            for i in range(len(lst)):
                if last_result != lst[i].result:
                    last_pos, last_result = i + 1, lst[i].result
                t.append([last_pos, lst[i].student_code, lst[i].result])
            top[cls] = t
        params['top'] = top
    except Exception:
        pass
    return params


def group_page_params(iti: Iti, subject: Subject):
    res = {'iti': iti, 'year': iti.id, 'subject': subject.id, 'h_sub_name': subject.name}
    try:
        ys = ItiSubject.select(iti.id, subject.id)
        if ys is None:
            raise ValueError()
        res['ys'] = ys
        teams = Team.select_by_iti(iti.id)
        for team in teams:
            gr = GroupResult.select_by_team_and_subject(team.id, subject.id)
            if gr is None:
                gr.result = 0
            res['t' + str(team.id)] = gr.result
    except Exception:
        pass
    return res


@app.route('/<int:iti_id>/<int:subject_id>/add_result')
@cross_origin()
@login_required
@check_access(block=True)
def add_result(iti: Iti, subject_id: int):
    try:
        subject = Subject.select(subject_id)
        if subject is None:
            raise ValueError()
    except Exception:
        return forbidden_error()
    ys = ItiSubject.select(iti.id, subject.id)
    if ys is None or not check_role(roles=[UserRoleItiSubject.ADD_RESULT], iti_id=iti.id, iti_subject_id=ys.id):
        return forbidden_error()

    if subject.type == 'i':
        params = individual_page_params(iti, subject)
        return render_template('add_result.html', **params, iti_id=iti.id, iti_subject_id=ys.id)
    else:
        params = group_page_params(iti, subject)
        return render_template(str(iti.id) + '/add_result.html', **params)


@app.route('/<int:iti_id>/<int:subject_id>/class_split_results')
@cross_origin()
@login_required
@check_access(block=True)
def class_split_results(iti: Iti, subject_id: int):
    try:
        subject = Subject.select(subject_id)
        if subject is None:
            raise ValueError()
    except Exception:
        return forbidden_error()

    params = individual_page_params(iti, subject)
    ys = ItiSubject.select(iti.id, subject.id)
    if not ys:
        return render_template('add_result.html', **params, error4='Такого предмета нет в этом году.')
    if not check_role(roles=[UserRoleItiSubject.SPLIT_CLASS], iti_id=iti.id, iti_subject_id=ys.id):
        return render_template('add_result.html', **params, error4='У вас не доступа к этому предмету')
    try:
        Generator.get_results_individual_subject(iti, ys.id)
    except ValueError as ex:
        return render_template('add_result.html', **params, error4=str(ex))
    return render_template('add_result.html', **params, error4='Школьники разделены по классам')


@app.route('/<int:iti_id>/<int:subject_id>/share_results')
@cross_origin()
@login_required
@check_access(block=True)
def share_results(iti: Iti, subject_id: int):
    try:
        subject = Subject.select(subject_id)
        if subject is None:
            raise ValueError()
    except Exception:
        return forbidden_error()

    params = individual_page_params(iti, subject)
    ys = ItiSubject.select(iti.id, subject.id)
    if ys is None:
        return render_template('add_result.html', **params, error3='Такого предмета нет в этом году.')
    if not check_role(roles=[UserRoleItiSubject.SHARE_RESULT], iti_id=iti.id, iti_subject_id=ys.id):
        return render_template('add_result.html', **params, error3='У вас не доступа к этому предмету')
    try:
        Generator.gen_individual_results(Iti.select(iti.id), subject.id, '{}/{}.html'.format(iti.id, subject.id))
    except ValueError as ex:
        return render_template('add_result.html', **params, error3=str(ex))
    message_results_public(iti.id, subject.id)
    return render_template('add_result.html', **params, error3='Результаты опубликованы')


@app.route("/<int:iti_id>/ratings_update")
@cross_origin()
@login_required
@check_access(roles=[UserRoleIti.ADMIN], block=True)
def ratings_update(iti: Iti):
    Generator.gen_ratings(iti)
    message_ratings_public(iti.id)
    return render_template(str(iti.id) + '/rating.html', error='Рейтинги обновлены', iti=iti)


@app.route('/<int:iti_id>/<int:subject_id>/share_group_results')
@cross_origin()
@login_required
@check_access(block=True)
def share_group_results(iti: Iti, subject_id: int):
    try:
        try:
            subject = Subject.select(subject_id)
            if subject is None:
                raise ValueError()
        except Exception:
            return forbidden_error()

        params = group_page_params(iti, subject)
        ys = ItiSubject.select(iti.id, subject.id)
        if ys is None:
            return render_template('/add_result.html', **params, error2='Такого предмета нет в этом году.')
        if not check_role(roles=[UserRoleItiSubject.SHARE_RESULT], iti_id=iti.id, iti_subject_id=ys.id):
            return render_template('/add_result.html', **params, error2='У вас не доступа к этому предмету')    
        Generator.gen_group_results(iti, subject.id, '{}/{}.html'.format(iti.id, subject.id))
        message_results_public(iti.id, subject.id)
        return render_template(str(iti.id) + '/add_result.html', **params, error2='Результаты опубликованы')
    except Exception as ex:
        import traceback
        return str(ex) + '<br><br>' + str(traceback.format_exc())


@app.route('/<int:iti_id>/share_all_results')
@cross_origin()
@login_required
@check_access(roles=[UserRoleIti.ADMIN], block=True)
def share_all_results(iti: Iti):
    try:
        ys = ItiSubject.select_by_iti(iti.id)
        url = str(iti.id) + '/rating.html'
        errors = []
        subjects = []
        for now in ys:
            subject = Subject.select(now.subject_id)
            subjects.append(subject)
            try:
                suf = str(subject.id) + '.html'
                if subject.type == 'i':
                    Generator.gen_individual_results(iti, subject.id, str(iti.id) + '/' + suf)
                else:
                    Generator.gen_group_results(iti, subject.id, str(iti.id) + '/' + suf)
            except ValueError:
                errors.append(subject.name)
        Generator.gen_ratings(iti)
        if errors:
            return render_template(url, error=', '.join(errors) + ' имеют неправильные результаты.', iti=iti)
        else:
            message_all_ratings_public(iti.id, subjects)
            return render_template(url, error='Рейтинги обновлены', iti=iti)
    except Exception as ex:
        import traceback
        return str(ex) + '<br><br>' + str(traceback.format_exc())
