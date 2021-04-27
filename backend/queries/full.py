from backend import app
from flask import render_template, request
from flask_cors import cross_origin
from flask_login import login_required
from .help import check_status
from backend.database import SubjectsTable, Subject, YearsTable, Year, YearsSubjectsTable, YearSubject
from .auto_generator import Generator
from .file_creator import FileCreator
'''
    Функции ниже доступны только full, если не указано иного.
    /add_year               add_year()              Создаёт новый год ИТИ.
    /add_subject            add_subject()           Создаёт новый предмет.
    /edit_subject           edit_subject()          Редактирует предмет.
    /delete_subject         delete_subject()        Удаляет предмет.
    /<year>/subject_year    subject_year(year)      Сопастовляет ИТИ и предметы.
'''


@app.route("/add_year", methods=['POST'])
@cross_origin()
@login_required
@check_status('full')
def add_year():
    name = int(request.form['name'])
    year = YearsTable.select_by_year(name)
    if not year.__is_none__:
        return render_template('subjects_and_years.html', error1='Год уже существует')
    year = Year([name])
    YearsTable.insert(year)
    FileCreator.create_year(name)
    Generator.gen_years_lists()
    Generator.gen_years_subjects_list(name)
    return render_template('subjects_and_years.html', error1='Год добавлен')


@app.route("/add_subject", methods=['POST'])
@cross_origin()
@login_required
@check_status('full')
def add_subject():
    name = request.form['name']
    subject_type = request.form['type']
    subject = SubjectsTable.select_by_name(name)
    if not subject.__is_none__:
        return render_template('subjects_and_years.html', error2='Предмет уже существует')
    subject = Subject([0, name, subject_type])
    SubjectsTable.insert(subject)
    Generator.gen_subjects_lists()
    return render_template('subjects_and_years.html', error2='Предмет добавлен')


@app.route("/edit_subject", methods=['POST'])
@cross_origin()
@login_required
@check_status('full')
def edit_subject():
    id = int(request.form['id'])
    new_name = request.form['new_name']
    subject_type = request.form['new_type']
    subject = SubjectsTable.select_by_id(id)
    if subject.__is_none__:
        return render_template('subjects_and_years.html',  error3='Предмета не существует')
    subject.name = new_name
    subject.type = subject_type
    SubjectsTable.update_by_id(subject)
    Generator.gen_subjects_lists()
    return render_template('subjects_and_years.html', error3='Предмет обнавлён')


@app.route("/delete_subject", methods=['POST'])
@cross_origin()
@login_required
@check_status('full')
def delete_subject():
    id = int(request.form['id'])
    subject = SubjectsTable.select_by_id(id)
    if subject.__is_none__:
        return render_template('subjects_and_years.html', error4='Предмета не существует')
    SubjectsTable.delete(subject)
    Generator.gen_subjects_lists()
    return render_template('subjects_and_years.html', error4='Предмет удалён')


@app.route("/<path:year>/subject_year", methods=['POST'])
@cross_origin()
@login_required
@check_status('admin')
def subject_year(year):
    year = int(year)
    subjects = request.form.getlist('subject')
    YearsSubjectsTable.delete_by_year(year)
    for subject in subjects:
        YearsSubjectsTable.insert(YearSubject([year, int(subject)]))
    FileCreator.create_subjects(year, subjects)
    Generator.gen_years_subjects_list(year)
    return render_template(str(year) + '/subjects_for_year.html', error='Сохранено', year=year)
