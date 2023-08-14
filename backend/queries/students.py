from backend import app
from .. import Config
from ..database import Barcode, Student, StudentClass, StudentCode, Year
from .help import check_status, check_block_year
from .auto_generator import Generator
from flask import render_template, send_file, request, jsonify
from flask_cors import cross_origin
from flask_login import login_required
import json
import os
from PIL import Image
from pyzbar import pyzbar
from random import sample
import time
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


def barcodes_from_image(image):
    decoded_objects = pyzbar.decode(image)
    ean8, ean13 = [], []
    for obj in decoded_objects:
        value = [obj.rect, obj.data.decode("utf-8")]
        if obj.type == 'EAN13':
            ean13.append(value)
        elif obj.type == 'EAN8':
            ean8.append(value)
    return ean8, ean13


@app.route("/<year:year>/save_barcodes", methods=['POST'])
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def save_barcodes(year: int):
    try:
        data = request.form['data']
        value = json.loads(data)
        for line in value:
            student_id = int(line[0])
            if not Student.select(student_id):
                raise ValueError('Школьника "{}" не существует'.format(student_id))
            for barcode in line[1:]:
                if barcode.isdigit():
                    bar = Barcode.select(year, int(barcode))
                    if bar and bar.student_id != student_id:
                        raise ValueError('Штрих-код "{}" уже сохранён на школьника "{}"'.format(barcode, student_id))
        for line in value:
            student_id = line[0]
            for barcode in line[1:]:
                if barcode.isdigit() and not Barcode.select(year, int(barcode)):
                    Barcode.insert(Barcode.build(year, int(barcode), student_id))
    except Exception as ex:
        return jsonify({'status': 'Error', 'msg': str(ex)})
    return jsonify({'status': 'OK'})


@app.route("/<year:year>/student_info", methods=['POST'])
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def student_info(year: int):
    student_id = request.form['student_id']
    student = Student.select(student_id)
    if not student:
        return jsonify({'status': 'Error'})
    student_class = StudentClass.select(year, student_id)
    if not student_class:
        return jsonify({'status': 'Error'})
    return jsonify({'status': 'OK', 'student': student.json(), 'student_class': student_class.json()})


@app.route("/<year:year>/upload_barcodes", methods=['POST'])
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def upload_barcodes(year: int):
    file = request.files['file']
    filename = Config.DATA_FOLDER + '/' + str(round(time.time() * 1000)) + '.' + file.filename.rsplit('.')[-1]
    # filename = 'backend/data/image.jpg'
    file.save(filename)
    img = Image.open(filename)
    ean8, ean13 = barcodes_from_image(img)
    groups, errors = [], []
    for code in ean8:
        val = [code[0].top, code[0].top + code[0].height, code[1]]
        groups.append(val)
    for code in ean13:
        pos = code[0].top + code[0].height // 2
        for ean8 in groups:
            if ean8[0] <= pos <= ean8[1]:
                ean8.append(code[1])
                break
        else:
            errors.append(code)
    groups.sort(key=lambda x: x[0] + x[1])
    new_groups = []
    for group in groups:
        student_id = int(group[2][:-1])
        student = Student.select(student_id)
        student_class = StudentClass.select(year, student_id)
        if not student:
            errors.append(group)
        current = [student.json(), student_class.json(), group[3:]]
        new_groups.append(current)
    os.remove(filename)
    return jsonify({'status': 'OK', 'groups': new_groups, 'errors': errors})


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
