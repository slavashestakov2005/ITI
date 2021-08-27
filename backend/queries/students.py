from backend import app
from ..database import StudentsTable, Student, StudentsCodesTable, StudentCode
from .help import check_status, check_block_year, split_class
from .auto_generator import Generator
from flask import render_template, request
from flask_cors import cross_origin
from flask_login import login_required
from random import shuffle
'''
    /registration_student   registration_student()      Регистрирует участника.
    /edit_student           edit_student()              Редактирует ученика.
    /delete_student         delete_student()            Удаляет ученика.
    /<year>/create_codes    create_codes()              Создаёт коды для участников (admin).
    /<year>/print_codes     print_codes()               Генерирует страницу с кодами всех участников (admin).
    /create_students_lists  create_students_lists()     Генериркет списки участников для всех классов (admin).
    /update_all_class_n     update_all_class_n()        Переводит всех школьников в следующий класс (full).
'''


@app.route('/registration_student', methods=['POST'])
@cross_origin()
@login_required
@check_block_year()
def registration_student():
    class_ = split_class(request.form['class'])
    student = Student([None, request.form['name1'], request.form['name2'], class_[0], class_[1]])
    s = StudentsTable.select_by_student(student)
    if not s.__is_none__:
        return render_template('student_edit.html', error1='Такой участник уже есть')
    StudentsTable.insert(student)
    Generator.gen_students_list(student.class_n)
    return render_template('student_edit.html', error1='Участник добавлен')


@app.route('/edit_student', methods=['POST'])
@cross_origin()
@login_required
@check_block_year()
def edit_student():
    class_old = split_class(request.form['o_class'])
    student_old = Student([None, request.form['o_name1'], request.form['o_name2'], class_old[0], class_old[1]])
    student_old = StudentsTable.select_by_student(student_old)
    rows = []
    if student_old.__is_none__:
        return render_template('student_edit.html', error2='Такого участника нет')
    rows.append(student_old.id)
    rows.append(request.form['n_name1'] if request.form['n_name1'] else student_old.name_1)
    rows.append(request.form['n_name2'] if request.form['n_name2'] else student_old.name_2)
    if request.form['n_class']:
        class_ = split_class(request.form['n_class'])
        rows.append(class_[0])
        rows.append(class_[1])
    else:
        rows.append(student_old.class_n)
        rows.append(student_old.class_l)
    s = Student(rows)
    StudentsTable.update(s)
    Generator.gen_students_list(student_old.class_n)
    Generator.gen_students_list(s.class_n)
    return render_template('student_edit.html', error2='Данные изменены')


@app.route('/delete_student', methods=['POST'])
@cross_origin()
@login_required
@check_block_year()
def delete_student():
    class_ = split_class(request.form['class'])
    student = Student([None, request.form['name1'], request.form['name2'], class_[0], class_[1]])
    student = StudentsTable.select_by_student(student)
    if student.__is_none__:
        return render_template('student_edit.html', error3='Такого участника нет')
    StudentsTable.delete(student)
    Generator.gen_students_list(student.class_n)
    return render_template('student_edit.html', error3='Участник удалён')


@app.route("/<path:year>/create_codes")
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def create_codes(year):
    year = int(year)
    students = StudentsTable.select_all()
    length = len(students)
    codes = [_ for _ in range(9999, 9999 - length, -1)]
    shuffle(codes)
    StudentsCodesTable.delete_by_year(year)
    for i in range(length):
        codes[i] = StudentCode([year, codes[i], students[i].id])
    StudentsCodesTable.insert_all(codes)
    return render_template(str(year) + '/codes.html', year=year, error='Коды сгенерированы')


@app.route("/<path:year>/print_codes")
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def print_codes(year):
    Generator.gen_codes(year)
    return render_template(year + '/codes.html', year=year, error='Таблица обновлена')


@app.route("/create_students_lists")
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def create_students_lists():
    for i in range(5, 10):
        Generator.gen_students_list(i)
    return render_template('student_edit.html', error4='Таблицы участников обновлены')


@app.route('/update_all_class_n')
@cross_origin()
@login_required
@check_status('full')
@check_block_year()
def update_all_class_n():
    StudentsTable.add_class()
    return render_template('student_edit.html', error4='Класс добавлен')
