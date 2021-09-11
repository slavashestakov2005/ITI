from backend import app
from ..database import TeamsTable, Team, StudentsTable, Student, TeamsStudentsTable, TeamStudent
from .help import check_status, check_block_year, split_class
from .auto_generator import Generator
from flask import render_template, request
from flask_cors import cross_origin
from flask_login import login_required
'''
    /<year>/add_team                add_team()                  Добавляет команду.
    /<year>/delete_team             delete_team()               Удаляет команду.
    /<year>/add_student_team        add_student_team()          Добавляет участника в команду.
    /<year>/delete_student_team     delete_student_team()       Удаляет участника из команды.
'''


@app.route("/<int:year>/add_team", methods=['POST'])
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def add_team(year: int):
    try:
        name = request.form['name']
        later = request.form['later']
    except Exception:
        return render_template(str(year) + '/subjects_for_year.html', error2='Некорректные данные')

    if not TeamsTable.select_by_year_and_later(year, later).__is_none__:
        return render_template(str(year) + '/subjects_for_year.html', error2='Команда от этой вертикали уже есть')
    TeamsTable.insert(Team([None, name, year, later]))
    Generator.gen_teams(year)
    return render_template(str(year) + '/subjects_for_year.html', error2='Команда добавлена')


@app.route("/<int:year>/delete_team", methods=['POST'])
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def delete_team(year: int):
    try:
        id = request.form['id']
    except Exception:
        return render_template(str(year) + '/subjects_for_year.html', error3='Некорректные данные')

    TeamsTable.delete(Team([id, '', year, '']))
    Generator.gen_teams(year)
    return render_template(str(year) + '/subjects_for_year.html', error3='Команда удалена')


@app.route("/<int:year>/add_student_team", methods=['POST'])
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def add_student_team(year: int):
    try:
        team = request.form['team']
        name1 = request.form['name1']
        name2 = request.form['name2']
        class_ = split_class(request.form['class'])
    except Exception:
        return render_template(str(year) + '/subjects_for_year.html', error4='Некорректные данные')

    if TeamsTable.select_by_id(team).__is_none__:
        return render_template(str(year) + '/subjects_for_year.html', error4='Такой команды нет')
    student = StudentsTable.select_by_student(Student([None, name1, name2, class_[0], class_[1]]))
    if student.__is_none__:
        return render_template(str(year) + '/subjects_for_year.html', error4='Такого участника нет')
    team_student = TeamStudent([team, student.id])
    if not TeamsStudentsTable.select(team_student).__is_none__:
        return render_template(str(year) + '/subjects_for_year.html', error4='Этот участник уже в этой команде')
    TeamsStudentsTable.insert(team_student)
    Generator.gen_teams_students(year)
    return render_template(str(year) + '/subjects_for_year.html', error4='Участник добавлен')


@app.route("/<int:year>/delete_student_team", methods=['POST'])
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def delete_student_team(year: int):
    try:
        team = request.form['team']
        name1 = request.form['name1']
        name2 = request.form['name2']
        class_ = split_class(request.form['class'])
    except Exception:
        return render_template(str(year) + '/subjects_for_year.html', error5='Некорректные данные')

    if TeamsTable.select_by_id(team).__is_none__:
        return render_template(str(year) + '/subjects_for_year.html', error5='Такой команды нет')
    student = StudentsTable.select_by_student(Student([None, name1, name2, class_[0], class_[1]]))
    if student.__is_none__:
        return render_template(str(year) + '/subjects_for_year.html', error5='Такого участника нет')
    team_student = TeamStudent([team, student.id])
    if TeamsStudentsTable.select(team_student).__is_none__:
        return render_template(str(year) + '/subjects_for_year.html', error5='Этого человека нет в этой команде')
    TeamsStudentsTable.delete(team_student)
    Generator.gen_teams_students(year)
    return render_template(str(year) + '/subjects_for_year.html', error5='Участник удалён')
