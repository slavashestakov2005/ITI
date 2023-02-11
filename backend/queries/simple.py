from backend import app
from flask import render_template, redirect, request
from flask_cors import cross_origin
from flask_login import current_user, login_required
from ..help.errors import forbidden_error, not_found_error
from .help import LOGIN_REQUIRED_FILES, STATUS_REQUIRED_FILES, current_year, split_class
from ..database import StudentsTable, Student, ResultsTable, YearsSubjectsTable, SubjectsTable, StudentsCodesTable, \
    Result, MessagesTable, YearsTable, Message
from jinja2 import TemplateNotFound
from itertools import permutations
import os
from ..config import Config
'''
    /                                   Возвращает стартовую страницу сайта.
    /<year>/                            Возвращает стартовую страницу года.
    /<year>/main.html                   Рисует стартовую страницу года.
    /admin_panel                        Рисует админ-панель.
    /<path>                             Возвращает статическую страницу, проверяя статус пользователя и доступ к файлу.
    /<year>/individual_tours.html       Ищет индивидуальные результаты участника по его имени.
'''


@app.route('/')
@cross_origin()
def index():
    y = current_year()
    if os.path.exists(Config.TEMPLATES_FOLDER + '/' + str(y) + '/main.html'):
        return redirect(str(y) + '/main.html')
    elif os.path.exists(Config.TEMPLATES_FOLDER + '/-' + str(y) + '/main.html'):
        return redirect('-' + str(y) + '/main.html')
    else:
        return forbidden_error()


@app.route('/<year:year>/')
@cross_origin()
def main_year_page_redirect(year: int):
    return redirect('/{}/main.html'.format(year))


@app.route('/admin_panel')
@cross_origin()
@login_required
def admin_panel():
    year, subject, sub = request.args.get('year'), request.args.get('subject'), []
    if subject:
        subject = SubjectsTable.select(subject)
        if subject.__is_none__:
            subject = None
    if year:
        for cur_sub in YearsSubjectsTable.select_by_year(year):
            sub.append(SubjectsTable.select(cur_sub.subject))
    return render_template('admin_panel.html', year=year, subject=subject, years=YearsTable.select_all(), subjects=sub)


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
            parts, params = path.split('/'), {}
            if parts[0][0] == '-':
                parts[0] = parts[0][1:]
            if parts[0].isdigit():
                params['year'] = parts[0]
            if parts[0] == 'Info' or parts[0] == '2019' or parts[0] == '2020':
                params['is_info'] = True
            return render_template(path, **params)
        return app.send_static_file(path)
    except TemplateNotFound:
        return not_found_error()


@app.route('/<year:year>/main.html')
@cross_origin()
def search(year: int):
    params, q = {'year': abs(year)}, request.args.get('q')
    if year == 2019 or year == 2020:
        params['is_info'] = True
    if q and q != '':
        q, data, days, summ = q.split(), [], {}, 0
        res_per = q
        if len(q) == 3:
            res_student = None
            for x in permutations(q):
                try:
                    student = Student([0, x[0], x[1], *split_class(x[2]), 0])
                    student = StudentsTable.select_by_student(student)
                    if not student.__is_none__:
                        if res_student:
                            res_student, res_per = None, q
                            break
                        else:
                            res_student, res_per = student, x
                except Exception:
                    pass
            if res_student:
                user = StudentsCodesTable.select_by_student(year, res_student.id)
                if not user.__is_none__:
                    for subject in YearsSubjectsTable.select_by_year(year):
                        code = user.code1 if subject.n_d == 1 else user.code2
                        r = ResultsTable.select_for_people(Result([year, subject.subject, code, 0, 0, '', 0]))
                        if not r.__is_none__ and r.position > 0:
                            data.append([SubjectsTable.select(subject.subject).name, r.position, r.text_result,
                                         r.result, r.net_score])
                            if subject.n_d not in days:
                                days[subject.n_d] = []
                            days[subject.n_d].append(r.net_score)
                for x in days.values():
                    summ += sum(sorted(x, reverse=True)[:2])
        elif len(q) == 1:
            try:
                student_code = int(q[0])
                users = StudentsCodesTable.select_by_code(year, student_code)
                for user in users:
                    if not user.__is_none__:
                        for subject in YearsSubjectsTable.select_by_year(year):
                            r = ResultsTable.select_for_people(Result([year, subject.subject, student_code, 0, 0, '', 0]))
                            if not r.__is_none__ and r.position > 0:
                                data.append([SubjectsTable.select(subject.subject).name, r.position, r.text_result,
                                             r.result, r.net_score])
                                if subject.n_d not in days:
                                    days[subject.n_d] = []
                                days[subject.n_d].append(r.net_score)
                        for x in days.values():
                            summ += sum(sorted(x, reverse=True)[:2])
            except Exception:
                pass
        params['search'] = ' '.join(res_per)
        params['searched_data'] = data
        params['empty'] = not bool(len(data))
        params['summ'] = summ
    else:
        params['messages'] = sorted(MessagesTable.select_by_year(year), key=Message.sort_by_time)
        params['years'] = YearsTable.select_all()
    try:
        return render_template(str(year) + '/main.html', **params)
    except TemplateNotFound:
        return not_found_error()
