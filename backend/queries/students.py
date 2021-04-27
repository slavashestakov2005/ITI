from backend import app
from ..database import StudentsTable, Student
from flask import render_template, request
from flask_cors import cross_origin
from flask_login import login_required
from time import time
'''
    /registration_student   registration_student()      Регистрирует участника.
    /edit_student           edit_student()              Редактирует ученика.
    /delete_student         delete_student()            Удаляет ученика.
'''


def split_class(class_):
    return int(class_[:-1]), class_[-1],


@app.route('/registration_student', methods=['POST'])
@cross_origin()
@login_required
def registration_student():
    class_ = split_class(request.form['class'])
    student = Student([request.form['last_name'], request.form['first_name'], class_[0], class_[1], int(time() * 10)])
    s = StudentsTable.select_by_student(student)
    if not s.__is_none__:
        return render_template('student_edit.html', error1='Такой участник уже есть')
    StudentsTable.insert(student)
    return render_template('student_edit.html', error1='Участник добавлен')


@app.route('/edit_student', methods=['POST'])
@cross_origin()
@login_required
def edit_student():
    class_old = split_class(request.form['o_class'])
    student_old = Student([request.form['o_name1'], request.form['o_name2'], class_old[0], class_old[1], int(time() * 10)])
    student_old = StudentsTable.select_by_student(student_old)
    rows = []
    if student_old.__is_none__:
        return render_template('student_edit.html', error2='Такого участника нет')
    rows.append(request.form['n_name1'] if request.form['n_name1'] else student_old.name_1)
    rows.append(request.form['n_name2'] if request.form['n_name2'] else student_old.name_2)
    if request.form['n_class']:
        class_ = split_class(request.form['n_class'])
        rows.append(class_[0])
        rows.append(class_[1])
    else:
        rows.append(student_old.class_n)
        rows.append(student_old.class_l)
    rows.append(student_old.code)
    s = Student(rows)
    StudentsTable.update_by_student(student_old, s)
    return render_template('student_edit.html', error2='Участник удалён')


@app.route('/delete_student', methods=['POST'])
@cross_origin()
@login_required
def delete_student():
    class_ = split_class(request.form['class'])
    student = Student([request.form['last_name'], request.form['first_name'], class_[0], class_[1], int(time() * 10)])
    s = StudentsTable.select_by_student(student)
    if s.__is_none__:
        return render_template('student_edit.html', error3='Такого участника нет')
    StudentsTable.delete(student)
    return render_template('student_edit.html', error3='Участник удалён')
