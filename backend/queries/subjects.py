from backend import app
from backend.help.errors import forbidden_error
from .help import check_status
from ..database import YearSubject, YearsSubjectsTable
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


@app.route("/<path:year>/subject_year", methods=['POST'])
@cross_origin()
@login_required
@check_status('admin')
def subject_year(year):
    year = int(year)
    subjects = request.form.getlist('subject')
    YearsSubjectsTable.delete_by_year(year)
    for subject in subjects:
        YearsSubjectsTable.insert(YearSubject([year, int(subject), 0, 0, 0, 0, 0, 0, 0, '']))
    FileCreator.create_subjects(year, subjects)
    Generator.gen_years_subjects_list(year)
    return render_template(str(year) + '/subjects_for_year.html', error1='Сохранено', year=year)


@app.route('/<path:path1>/<path:path2>/<path:path3>/max_score', methods=['POST'])
@cross_origin()
@login_required
def max_score(path1, path2, path3):
    subject = int(path3[:-5])
    year = int(path1)
    if not current_user.can_do(subject):
        return forbidden_error()
    if YearsSubjectsTable.select(year, subject).__is_none__:
        return render_template('add_result.html', **page_params(path1, path2, path3),
                               error0='Такого предмета в этом году нет')
    s5 = request.form['score_5'] if request.form['score_5'] else 0
    s6 = request.form['score_6'] if request.form['score_6'] else 0
    s7 = request.form['score_7'] if request.form['score_7'] else 0
    s8 = request.form['score_8'] if request.form['score_8'] else 0
    s9 = request.form['score_9'] if request.form['score_9'] else 0
    YearsSubjectsTable.update(YearSubject([year, subject, s5, s6, s7, s8, s9]))
    return render_template('add_result.html', **page_params(path1, path2, path3), error1='Обновлено')


@app.route('/<path:year>/subject_description', methods=['POST'])
@cross_origin()
@login_required
@check_status('admin')
def subject_description(year):
    year = int(year)
    subject = int(request.form['subject'])
    place = request.form['place']
    date = [int(_) for _ in request.form['date'].split('-')]
    start = [int(_) for _ in request.form['start'].split(':')]
    end = [int(_) for _ in request.form['end'].split(':')]
    start = int(datetime(*date, *start).timestamp())
    end = int(datetime(*date, *end).timestamp())
    year_subject = YearsSubjectsTable.select(year, subject)
    if year_subject.__is_none__:
        return render_template(str(year) + '/subjects_for_year.html', error6='Этого предмета нет в этом году.')
    year_subject.start = start
    year_subject.end = end
    year_subject.place = place
    YearsSubjectsTable.update(year_subject)
    Generator.gen_timetable(year)
    return render_template(str(year) + '/subjects_for_year.html', error6='Сохранено.')
