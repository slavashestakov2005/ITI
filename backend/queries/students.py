from backend import app
from ..database import Student, StudentCode, Year
from .help import check_status, check_block_year
from .auto_generator import Generator
from flask import render_template, send_file
from flask_cors import cross_origin
from flask_login import login_required
from random import sample
'''
    /<year>/create_codes            create_codes()              Создаёт коды для участников (admin).
    /<year>/print_codes             print_codes()               Генерирует страницу с кодами всех участников (admin).
    /<year>/get_codes               get_codes()                 Возвращает Excel таблицу с годовой кодировкой (admin).
    /<year>/create_students_lists   create_students_lists()     Генерирует списки участников для всех классов (admin).
'''


@app.route("/<year:year>/create_codes")
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def create_codes(year: int):
    if Year.select(year) is None:
        return render_template(str(year) + '/codes.html', year=abs(year), error='Этого года нет.')
    students = Student.select_by_year(year)
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
    return send_file(filename, as_attachment=True, download_name='ИТИ {}. Кодировка.xlsx'.format(year))


@app.route("/<year:year>/create_students_lists")
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def create_students_lists(year: int):
    year_info = Year.select(year)
    if year_info is None:
        return render_template('student_edit.html', error4='Такого года ИТИ нет', year=year, year_info=year_info)
    for class_num in year_info.classes:
        Generator.gen_students_list(year, int(class_num))
    return render_template('student_edit.html', error4='Таблицы участников обновлены', year=year, year_info=year_info)
