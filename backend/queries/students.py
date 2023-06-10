from backend import app
from ..database import Student, StudentCode, Year
from .help import check_status, check_block_year
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
    /create_students_lists  create_students_lists()     Генерирует списки участников для всех классов (admin).
    /update_all_class_n     update_all_class_n()        Переводит всех школьников в следующий класс (full).
'''


@app.route("/<year:year>/create_codes")
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def create_codes(year: int):
    if Year.select(year) is None:
        return render_template(str(year) + '/codes.html', year=abs(year), error='Этого года нет.')
    students = Student.select_all(year)
    length = len(students)
    codes1 = sample(range(1000, 10000), length)
    codes2 = codes1
    # if year > 0 else sample(range(1000, 10000), length) # НШ передумала :)
    StudentCode.delete_by_year(year)
    for i in range(length):
        codes1[i] = StudentCode.build(year, codes1[i], codes2[i], students[i].id)
    StudentCode.insert_all(codes1)
    return render_template(str(year) + '/codes.html', year=abs(year), error='Коды сгенерированы')


@app.route("/<year:year>/print_codes")
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def print_codes(year: int):
    if Year.select(year) is None:
        return render_template(str(year) + '/codes.html', year=abs(year), error='Этого года нет.')
    Generator.gen_codes(year)
    return render_template(str(year) + '/codes.html', year=abs(year), error='Таблица обновлена')


@app.route("/<year:year>/get_codes")
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def get_codes(year: int):
    if Year.select(year) is None:
        return render_template(str(year) + '/codes.html', year=abs(year), error='Этого года нет.')
    filename = './data/codes_{}.xlsx'.format(year)
    return send_file(filename, as_attachment=True, attachment_filename='Кодировка ИТИ {}.xlsx'.format(year))


@app.route("/create_students_lists")
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def create_students_lists():
    for i in range(2, 10):
        Generator.gen_students_list(i)
    return render_template('student_edit.html', error4='Таблицы участников обновлены')


@app.route('/update_all_class_n')
@cross_origin()
@login_required
@check_status('full')
@check_block_year()
def update_all_class_n():
    Student.add_class()
    return render_template('student_edit.html', error4='Класс добавлен')
