from backend import app
from flask import render_template, request
from flask_cors import cross_origin
from flask_login import login_required
from .help import check_status
from backend.database import SubjectsTable, Subject, YearsTable, Year
from .auto_generate import Generate


@app.route("/add_year", methods=['POST'])
@cross_origin()
@login_required
@check_status('admin')
def add_year():
    name = int(request.form['name'])
    year = YearsTable.select_by_year(name)
    if not year.__is_none__:
        return render_template('subjects_and_years.html', error1='Год уже существует')
    year = Year([name])
    YearsTable.insert(year)
    Generate.gen_years_lists()
    return render_template('subjects_and_years.html', error1='Год добавлен')


@app.route("/add_subject", methods=['POST'])
@cross_origin()
@login_required
@check_status('admin')
def add_subject():
    name = request.form['name']
    subject_type = request.form['type']
    subject = SubjectsTable.select_by_name(name)
    if not subject.__is_none__:
        return render_template('subjects_and_years.html', error2='Предмет уже существует')
    subject = Subject([0, name, subject_type])
    SubjectsTable.insert(subject)
    Generate.gen_subjects_lists()
    return render_template('subjects_and_years.html', error2='Предмет добавлен')


@app.route("/edit_subject", methods=['POST'])
@cross_origin()
@login_required
@check_status('admin')
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
    Generate.gen_subjects_lists()
    return render_template('subjects_and_years.html', error3='Предмет обнавлён')


@app.route("/delete_subject", methods=['POST'])
@cross_origin()
@login_required
@check_status('admin')
def delete_subject():
    id = int(request.form['id'])
    subject = SubjectsTable.select_by_id(id)
    if subject.__is_none__:
        return render_template('subjects_and_years.html', error4='Предмета не существует')
    SubjectsTable.delete(subject)
    Generate.gen_subjects_lists()
    return render_template('subjects_and_years.html', error4='Предмет удалён')

