from backend import app
from backend.help.errors import forbidden_error
from .help import check_status, check_block_year, path_to_subject, pref_year
from .messages_help import message_timetable_public
from ..database import Message, Subject, Year, YearSubject
from .results import page_params, tour_name
from .auto_generator import Generator
from .file_creator import FileCreator
from flask import render_template, request
from flask_cors import cross_origin
from flask_login import login_required, current_user
from datetime import datetime
'''
    /<year>/subject_year                    subject_year(year)          Сопоставляет ИТИ и предметы.
    /<path1>/<path3>/max_score              max_score(...)              Сохраняет максимальные баллы по предмету.
    /<year>/subject_description             subject_description(...)    Сохраняет описание предмета (время и место).
'''


def page_args(year: int):
    return {'year': abs(year), 'messages': Message.select_by_year(year)}


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

    if Year.select(year) is None:
        return render_template(str(year) + '/subjects_for_year.html', error1='Этого года нет.', **page_args(year))
    old_sub = [x.subject for x in YearSubject.select_by_year(year)]
    subjects = [int(_) for _ in subjects]
    for x in old_sub:
        if x not in subjects:
            YearSubject.delete(year, x)
    for x in subjects:
        if x not in old_sub:
            d = 30 if year > 0 else 0
            YearSubject.insert(YearSubject.build(year, x, 30, 30, 30, d, d, 0, 0, '', '', 0))
    FileCreator.create_subjects(year, subjects)
    Generator.gen_years_subjects_list(year)
    return render_template(str(year) + '/subjects_for_year.html', error1='Сохранено', **page_args(year))


@app.route('/<year:year>/<path:path3>/max_score', methods=['POST'])
@cross_origin()
@login_required
@check_block_year()
def max_score(year: int, path3):
    url = pref_year(year) + 'add_result.html'
    try:
        subject = path_to_subject(path3)
        subject = Subject.select(subject)
        if subject is None:
            raise ValueError()
    except Exception:
        return render_template(url, error1='Некорректные данные')
    params = page_params(year, tour_name(subject.type), path3)
    if not current_user.can_do(subject.id):
        return forbidden_error()
    ys = YearSubject.select(year, subject.id)
    if ys is None:
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

    YearSubject.update(YearSubject.build(year, subject.id, s5, s6, s7, s8, s9, ys.start, ys.end, ys.classes, ys.place, ys.n_d))
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
    year_subject = YearSubject.select(year, subject)
    if year_subject is None:
        return render_template(str(year) + '/subjects_for_year.html', error6='Этого предмета нет в этом году.', **page_args(year))
    year_subject.start = start
    year_subject.end = end
    year_subject.classes = classes
    year_subject.place = place
    year_subject.n_d = n_d
    YearSubject.update(year_subject)
    Generator.gen_timetable(year)
    Generator.gen_years_subjects_list(year)
    return render_template(str(year) + '/subjects_for_year.html', error6='Сохранено.', **page_args(year))


@app.route('/<year:year>/public_description')
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def public_description(year: int):
    if Year.select(year) is None:
        return render_template(str(year) + '/subjects_for_year.html', error11='Такого года нет.', **page_args(year))
    message_timetable_public(year)
    return render_template(str(year) + '/subjects_for_year.html', error11='Сообщение опубликовано', **page_args(year))
