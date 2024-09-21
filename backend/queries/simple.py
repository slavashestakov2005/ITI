from flask import redirect, render_template, request
from flask_cors import cross_origin
from flask_login import login_required
from itertools import permutations
from jinja2 import TemplateNotFound
import os
from werkzeug.exceptions import NotFound

from backend import app
from .help import split_class
from ..config import Config
from ..database import get_student_by_params, Message, Iti, ItiSubject, Result, Student, Subject
from ..help.errors import forbidden_error, not_found_error

'''
    /                                       Возвращает стартовую страницу последнего ИТИ.
    /<iti_id>/                              Возвращает стартовую страницу ИТИ.
    /admin_panel                            Рисует админ-панель.
    /<path>                                 Возвращает статическую страницу, проверяя статус пользователя и доступ к файлу.
    /<iti_id>/main                          Рисует стартовую страницу ИТИ.
'''


@app.route('/')
@cross_origin()
def index():
    iti = Iti.select_last()
    if iti and os.path.exists(Config.TEMPLATES_FOLDER + '/' + str(iti.id) + '/main.html'):
        return redirect(str(iti.id) + '/main')
    else:
        return forbidden_error()


@app.route('/<int:year>/')
@cross_origin()
def main_year_page_redirect(year: int):
    return redirect('/{}/main'.format(year))


@app.route('/admin_panel')
@cross_origin()
@login_required
def admin_panel():
    iti, subject, sub = request.args.get('year'), request.args.get('subject'), []
    if subject:
        ys = ItiSubject.select_by_id(subject)
        info = Subject.select(ys.subject_id) if ys is not None else None
        subject = {'subject': info, 'iti_subject': ys}
    if iti:
        for cur_sub in ItiSubject.select_by_iti(iti):
            sub.append({'info': Subject.select(cur_sub.subject_id), 'id': cur_sub.id})
        iti = Iti.select(iti)
    return render_template('admin_panel.html', iti=iti, subject=subject, itis=Iti.select_all(), subjects=sub)


@app.route('/Info/<path:path>')
@cross_origin()
def info_file(path):
    try:
        return render_template('Info/' + path)
    except TemplateNotFound:
        return not_found_error()


@app.route('/<path:path>')
@cross_origin()
def static_file(path):
    try:
        return app.send_static_file(path)
    except NotFound:
        return not_found_error()


def get_info_for_student(student: Student, year: int):
    data, days, summ = [], {}, 0
    for r in Result.select_for_student(student.id):
        if r.position > 0:
            ys = ItiSubject.select_by_id(r.iti_subject_id)
            if ys.iti_id == year:
                data.append([Subject.select(ys.subject_id).name, r.position, r.result, r.net_score])
                if ys.n_d not in days:
                    days[ys.n_d] = []
                days[ys.n_d].append(r.net_score)
    for x in days.values():
        summ += sum(sorted(x, reverse=True)[:2])
    return data, days, summ


@app.route('/<int:iti_id>/main')
@cross_origin()
def search(iti_id: int):
    iti = Iti.select(iti_id)
    if not iti:
        return forbidden_error()
    params, q = {'iti': iti}, request.args.get('q')
    if iti.id == 1 or iti.id == 2:
        params['is_info'] = True
    if q and q != '':
        q, data, days, summ = q.split(), [], {}, 0
        res_per = q
        if len(q) == 3:
            res_student = None
            for x in permutations(q):
                try:
                    student = get_student_by_params(iti.id, x[0], x[1], *split_class(x[2]))
                    if student is not None:
                        if res_student:
                            res_student, res_per = None, q
                            break
                        else:
                            res_student, res_per = student, x
                except Exception:
                    pass
            if res_student:
                data, days, summ = get_info_for_student(res_student, iti.id)
        elif len(q) == 1:
            try:
                student_code = int(q[0])
                student = Student.select(student_code)
                if student:
                    data, days, summ = get_info_for_student(student, iti.id)
            except Exception:
                pass
        params['search'] = ' '.join(res_per)
        params['searched_data'] = data
        params['empty'] = not bool(len(data))
        params['summ'] = summ
    else:
        params['messages'] = sorted(Message.select_by_iti(iti.id), key=Message.sort_by_time)
        params['itis'] = Iti.select_all()
    try:
        return render_template(str(iti.id) + '/main.html', **params)
    except TemplateNotFound:
        return not_found_error()
