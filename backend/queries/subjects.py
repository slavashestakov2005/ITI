from backend import app
from backend.help.errors import forbidden_error
from .help import check_status, check_block_year, path_to_subject, pref_year
from .messages_help import message_timetable_public
from ..database import YearSubject, YearsSubjectsTable, YearsTable, MessagesTable
from .results import page_params
from .auto_generator import Generator
from .file_creator import FileCreator
from flask import render_template, request
from flask_cors import cross_origin
from flask_login import login_required, current_user
from datetime import datetime
'''
    /<year>/subject_year                    subject_year(year)          Сопастовляет ИТИ и предметы.
    /<path1>/<path2>/<path3>/max_score      max_score(...)              Сохраняет максимальные баллы по предмету.
    /<year>/subject_description             subject_description(...)    Сохраняет описание предмета (время и место).
'''


def page_args(year: int):
    return {'year': abs(year), 'messages': MessagesTable.select_by_year(year)}


@app.route("/<year:year>/subject_year", methods=['POST'])
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def subject_year(year: int):
    try:
        subjects = request.form.getlist('subject')
    except Exception:
        return render_template(str(year) + '/subjects_for_year.html', error1='Некорректные данные', **page_args(year))

    if YearsTable.select(year).__is_none__:
        return render_template(str(year) + '/subjects_for_year.html', error1='Этого года нет.', **page_args(year))
    old_sub = [x.subject for x in YearsSubjectsTable.select_by_year(year)]
    subjects = [int(_) for _ in subjects]
    for x in old_sub:
        if x not in subjects:
            YearsSubjectsTable.delete(year, x)
    for x in subjects:
        if x not in old_sub:
            d = 30 if year > 0 else 0
            YearsSubjectsTable.insert(YearSubject([year, x, 30, 30, 30, d, d, 0, 0, '', '', 0]))
    FileCreator.create_subjects(year, subjects)
    Generator.gen_years_subjects_list(year)
    return render_template(str(year) + '/subjects_for_year.html', error1='Сохранено', **page_args(year))


@app.route('/<year:year>/<path:path2>/<path:path3>/max_score', methods=['POST'])
@cross_origin()
@login_required
@check_block_year()
def max_score(year: int, path2, path3):
    params = page_params(year, path2, path3)
    url = pref_year(year) + 'add_result.html'
    try:
        subject = path_to_subject(path3)
    except Exception:
        return render_template(url, **params, error1='Некорректные данные')

    if not current_user.can_do(subject):
        return forbidden_error()
    ys = YearsSubjectsTable.select(year, subject)
    if ys.__is_none__:
        return render_template(url, **params, error1='Такого предмета в этом году нет')

    try:
        if year > 0:
            s5 = request.form['score_5'] if request.form['score_5'] else 0
            s6 = request.form['score_6'] if request.form['score_6'] else 0
            s7 = request.form['score_7'] if request.form['score_7'] else 0
            s8 = request.form['score_8'] if request.form['score_8'] else 0
            s9 = request.form['score_9'] if request.form['score_9'] else 0
        else:
            s5 = request.form['score_2'] if request.form['score_2'] else 0
            s6 = request.form['score_3'] if request.form['score_3'] else 0
            s7 = request.form['score_4'] if request.form['score_4'] else 0
            s8 = s9 = 0
    except Exception:
        return render_template(url, **params, error1='Некорректные данные')

    YearsSubjectsTable.update(YearSubject([year, subject, s5, s6, s7, s8, s9, ys.start, ys.end, ys.classes, ys.place, ys.n_d]))
    return render_template(url, **params, error1='Обновлено')


@app.route('/<year:year>/subject_description', methods=['POST'])
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def subject_description(year: int):
    try:
        subject = int(request.form['subject'])
        classes = request.form['classes']
        place = request.form['place']
        date = [int(_) for _ in request.form['date'].split('-')]
        start = [int(_) for _ in request.form['start'].split(':')]
        end = [int(_) for _ in request.form['end'].split(':')]
        n_d = int(request.form['n_d'])
        if n_d <= 0:
            raise ValueError
    except Exception:
        return render_template(str(year) + '/subjects_for_year.html', error6='Некорректные данные', **page_args(year))

    start = int(datetime(*date, *start).timestamp())
    end = int(datetime(*date, *end).timestamp())
    year_subject = YearsSubjectsTable.select(year, subject)
    if year_subject.__is_none__:
        return render_template(str(year) + '/subjects_for_year.html', error6='Этого предмета нет в этом году.', **page_args(year))
    year_subject.start = start
    year_subject.end = end
    year_subject.classes = classes
    year_subject.place = place
    year_subject.n_d = n_d
    YearsSubjectsTable.update(year_subject)
    Generator.gen_timetable(year)
    Generator.gen_years_subjects_list(year)
    return render_template(str(year) + '/subjects_for_year.html', error6='Сохранено.', **page_args(year))


@app.route('/<year:year>/public_description')
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def public_description(year: int):
    if YearsTable.select(year).__is_none__:
        return render_template(str(year) + '/subjects_for_year.html', error11='Такого года нет.', **page_args(year))
    message_timetable_public(year)
    return render_template(str(year) + '/subjects_for_year.html', error11='Сообщение опубликовано', **page_args(year))
