from backend import app
from ..database import StudentsTable, Student, StudentsCodesTable, StudentCode, YearsTable
from .help import check_status, check_block_year, split_class, empty_checker
from .auto_generator import Generator
from flask import render_template, request, send_file
from flask_cors import cross_origin
from flask_login import login_required
from random import sample
'''
    /registration_student   registration_student()      Регистрирует участника.
    /edit_student           edit_student()              Редактирует ученика.
    /delete_student         delete_student()            Удаляет ученика.
    /<year>/create_codes    create_codes()              Создаёт коды для участников (admin).
    /<year>/print_codes     print_codes()               Генерирует страницу с кодами всех участников (admin).
    /<year>/get_codes       get_codes()                 Возвращает Excel таблицу с годовой кодировкой (admin).
    /create_students_lists  create_students_lists()     Генериркет списки участников для всех классов (admin).
    /update_all_class_n     update_all_class_n()        Переводит всех школьников в следующий класс (full).
'''


@app.route('/registration_student', methods=['POST'])
@cross_origin()
@login_required
@check_block_year()
def registration_student():
    try:
        class_ = split_class(request.form['class'])
        name1, name2 = request.form['name1'].capitalize(), request.form['name2'].capitalize()
        empty_checker(name1, name2)
        student = Student([None, name1, name2, class_[0], class_[1].capitalize()])
    except Exception:
        return render_template('student_edit.html', error1='Некорректные данные')

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
    try:
        class_old = split_class(request.form['o_class'])
        o_name1, o_name2 = request.form['o_name1'].capitalize(), request.form['o_name2'].capitalize()
        empty_checker(o_name1, o_name2)
        student_old = Student([None, o_name1, o_name2, class_old[0], class_old[1].capitalize()])
    except Exception:
        return render_template('student_edit.html', error2='Некорректные данные')

    student_old = StudentsTable.select_by_student(student_old)
    rows = []
    if student_old.__is_none__:
        return render_template('student_edit.html', error2='Такого участника нет')
    rows.append(student_old.id)

    try:
        rows.append(request.form['n_name1'].capitalize() if request.form['n_name1'] else student_old.name_1)
        rows.append(request.form['n_name2'].capitalize() if request.form['n_name2'] else student_old.name_2)
        if request.form['n_class']:
            class_ = split_class(request.form['n_class'])
            rows.append(class_[0])
            rows.append(class_[1].capitalize())
        else:
            rows.append(student_old.class_n)
            rows.append(student_old.class_l)
        empty_checker(rows[1], rows[2])
    except Exception:
        return render_template('student_edit.html', error2='Некорректные данные')

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
    try:
        class_ = split_class(request.form['class'])
        name1, name2 = request.form['name1'].capitalize(), request.form['name2'].capitalize()
        empty_checker(name1, name2)
        student = Student([None, name1, name2, class_[0], class_[1].capitalize()])
    except Exception:
        return render_template('student_edit.html', error3='Некорректные данные')

    student = StudentsTable.select_by_student(student)
    if student.__is_none__:
        return render_template('student_edit.html', error3='Такого участника нет')
    StudentsTable.delete(student)
    Generator.gen_students_list(student.class_n)
    return render_template('student_edit.html', error3='Участник удалён')


@app.route("/<int:year>/create_codes")
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def create_codes(year: int):
    if YearsTable.select_by_year(year).__is_none__:
        return render_template(str(year) + '/codes.html', year=year, error='Этого года нет.')
    students = StudentsTable.select_all()
    length = len(students)
    codes = sample(range(1000, 10000), length)
    StudentsCodesTable.delete_by_year(year)
    for i in range(length):
        codes[i] = StudentCode([year, codes[i], students[i].id])
    StudentsCodesTable.insert_all(codes)
    return render_template(str(year) + '/codes.html', year=year, error='Коды сгенерированы')


@app.route("/<int:year>/print_codes")
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def print_codes(year: int):
    if YearsTable.select_by_year(year).__is_none__:
        return render_template(str(year) + '/codes.html', year=year, error='Этого года нет.')
    Generator.gen_codes(year)
    return render_template(str(year) + '/codes.html', year=year, error='Таблица обновлена')


@app.route("/<int:year>/get_codes")
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def get_codes(year: int):
    if YearsTable.select_by_year(year).__is_none__:
        return render_template(str(year) + '/codes.html', year=year, error='Этого года нет.')
    filename = './data/codes_{}.xlsx'.format(year)
    return send_file(filename, as_attachment=True, attachment_filename='Кодировка ИТИ {}.xlsx'.format(year))


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
