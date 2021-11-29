from backend import app
from backend.help.errors import forbidden_error
from .help import check_status, check_block_year, correct_new_line, path_to_subject, SplitFile
from ..database import YearSubject, YearsSubjectsTable, YearsTable
from .results import page_params
from .auto_generator import Generator
from .file_creator import FileCreator
from ..config import Config
from flask import render_template, request
from flask_cors import cross_origin
from flask_login import login_required, current_user
from datetime import datetime
'''
    /<year>/subject_year                    subject_year(year)          Сопастовляет ИТИ и предметы.
    /<path1>/<path2>/<path3>/max_score      max_score(...)              Сохраняет максимальные баллы по предмету.
    /<year>/subject_description             subject_description(...)    Сохраняет описание предмета (время и место).
    /<year>/year_message                    year_message(...)           Сохраняет годовое объявление.
'''


@app.route("/<int:year>/subject_year", methods=['POST'])
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def subject_year(year: int):
    try:
        subjects = request.form.getlist('subject')
    except Exception:
        return render_template(str(year) + '/subjects_for_year.html', error1='Некорректные данные', year=year)

    if YearsTable.select_by_year(year).__is_none__:
        return render_template(str(year) + '/subjects_for_year.html', error1='Этого года нет.', year=year)
    old_sub = [x.subject for x in YearsSubjectsTable.select_by_year(year)]
    subjects = [int(_) for _ in subjects]
    for x in old_sub:
        if x not in subjects:
            YearsSubjectsTable.delete(year, x)
    for x in subjects:
        if x not in old_sub:
            YearsSubjectsTable.insert(YearSubject([year, x, 30, 30, 30, 30, 30, 0, 0, '', '', 0]))
    FileCreator.create_subjects(year, subjects)
    Generator.gen_years_subjects_list(year)
    return render_template(str(year) + '/subjects_for_year.html', error1='Сохранено', year=year)


@app.route('/<int:year>/<path:path2>/<path:path3>/max_score', methods=['POST'])
@cross_origin()
@login_required
@check_block_year()
def max_score(year: int, path2, path3):
    params = page_params(year, path2, path3)
    try:
        subject = path_to_subject(path3)
    except Exception:
        return render_template('add_result.html', **params, error1='Некорректные данные')

    if not current_user.can_do(subject):
        return forbidden_error()
    ys = YearsSubjectsTable.select(year, subject)
    if ys.__is_none__:
        return render_template('add_result.html', **params, error1='Такого предмета в этом году нет')

    try:
        s5 = request.form['score_5'] if request.form['score_5'] else 0
        s6 = request.form['score_6'] if request.form['score_6'] else 0
        s7 = request.form['score_7'] if request.form['score_7'] else 0
        s8 = request.form['score_8'] if request.form['score_8'] else 0
        s9 = request.form['score_9'] if request.form['score_9'] else 0
    except Exception:
        return render_template('add_result.html', **params, error1='Некорректные данные')

    YearsSubjectsTable.update(YearSubject([year, subject, s5, s6, s7, s8, s9, ys.start, ys.end, ys.classes, ys.place, ys.n_d]))
    return render_template('add_result.html', **params, error1='Обновлено')


@app.route('/<int:year>/subject_description', methods=['POST'])
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
    except Exception:
        return render_template(str(year) + '/subjects_for_year.html', error6='Некорректные данные')

    start = int(datetime(*date, *start).timestamp())
    end = int(datetime(*date, *end).timestamp())
    year_subject = YearsSubjectsTable.select(year, subject)
    if year_subject.__is_none__:
        return render_template(str(year) + '/subjects_for_year.html', error6='Этого предмета нет в этом году.')
    year_subject.start = start
    year_subject.end = end
    year_subject.classes = classes
    year_subject.place = place
    year_subject.n_d = n_d
    YearsSubjectsTable.update(year_subject)
    Generator.gen_timetable(year)
    Generator.gen_years_subjects_list(year)
    return render_template(str(year) + '/subjects_for_year.html', error6='Сохранено.')


@app.route('/<int:year>/year_message', methods=['POST'])
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def year_message(year: int):
    try:
        message = correct_new_line(request.form['file_text'])
    except Exception:
        return render_template(str(year.year) + '/subjects_for_year.html', error7='Некорректные данные', year=year.year)

    year = YearsTable.select_by_year(year)
    if year.__is_none__:
        return render_template(str(year.year) + '/subjects_for_year.html', error7='Этого года нет.', year=year.year)
    year.message = message
    YearsTable.update(year)
    data = SplitFile(Config.TEMPLATES_FOLDER + '/' + str(year.year) + '/subjects_for_year.html')
    data.insert_after_comment(' message ', '''<textarea name="file_text" id="file_text" placeholder="Объявление пусто"
    oninput="textInput(document, 'file_text')">{0}</textarea>'''.format(year.message))
    data.save_file()
    data = SplitFile(Config.TEMPLATES_FOLDER + '/' + str(year.year) + '/timetable.html')
    data.insert_after_comment(' message ', '\n<center><h1>Объявления</h1></center>\n{0}\n'.format(year.message)
                                            if year.message else '')
    data.save_file()
    return render_template(str(year.year) + '/subjects_for_year.html', error7='Сохранено.', year=year.year)
