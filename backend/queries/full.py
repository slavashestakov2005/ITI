from backend import app
from flask import render_template, request
from flask_cors import cross_origin
from flask_login import login_required
from .help import check_status
from backend.database import SubjectsTable, Subject, YearsTable, Year


@app.route("/subjects_and_years")
@cross_origin()
@login_required
@check_status('admin')
def subjects_and_years():
    subjects = SubjectsTable.select_all()
    return render_template('subjects_and_years.html', subjects=subjects)


@app.route("/add_year", methods=['POST'])
@cross_origin()
@login_required
@check_status('admin')
def add_year():
    name = int(request.form['name'])
    year = YearsTable.select_by_year(name)
    subjects = SubjectsTable.select_all()
    if not year.__is_none__:
        return render_template('subjects_and_years.html', subjects=subjects, error1='Год уже существует')
    year = Year([name])
    YearsTable.insert(year)
    return render_template('subjects_and_years.html', subjects=subjects, error1='Год добавлен')


@app.route("/add_subject", methods=['POST'])
@cross_origin()
@login_required
@check_status('admin')
def add_subject():
    name = request.form['name']
    subject = SubjectsTable.select_by_name(name)
    if not subject.__is_none__:
        subjects = SubjectsTable.select_all()
        return render_template('subjects_and_years.html', subjects=subjects, error2='Предмет уже существует')
    subject = Subject([0, name])
    SubjectsTable.insert(subject)
    subjects = SubjectsTable.select_all()
    return render_template('subjects_and_years.html', subjects=subjects, error2='Предмет добавлен')


@app.route("/edit_subject", methods=['POST'])
@cross_origin()
@login_required
@check_status('admin')
def edit_subject():
    id = int(request.form['id'])
    new_name = request.form['new_name']
    subject = SubjectsTable.select_by_id(id)
    if subject.__is_none__:
        subjects = SubjectsTable.select_all()
        return render_template('subjects_and_years.html', subjects=subjects, error3='Предмета не существует')
    subject.name = new_name
    SubjectsTable.update_by_id(subject)
    subjects = SubjectsTable.select_all()
    return render_template('subjects_and_years.html', subjects=subjects, error3='Предмет обнавлён')


@app.route("/delete_subject", methods=['POST'])
@cross_origin()
@login_required
@check_status('admin')
def delete_subject():
    id = int(request.form['id'])
    subject = SubjectsTable.select_by_id(id)
    if subject.__is_none__:
        subjects = SubjectsTable.select_all()
        return render_template('subjects_and_years.html', subjects=subjects, error4='Предмета не существует')
    SubjectsTable.delete(subject)
    subjects = SubjectsTable.select_all()
    return render_template('subjects_and_years.html', subjects=subjects, error4='Предмет удалён')

