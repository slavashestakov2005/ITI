from backend import app
from .. import Config
from ..database import Barcode, Student, StudentClass, Iti, School
from .help import check_status, check_block_iti
from flask import render_template, send_file, request, jsonify
from flask_cors import cross_origin
from flask_login import login_required

from glob import glob
import json
import os
from PIL import Image
from pyzbar import pyzbar
import time
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
from docx import Document
from docxcompose.composer import Composer
import barcode
from barcode.writer import ImageWriter
from docx2pdf import convert
import pythoncom


def create_empty_barcode_blank():
    return {}


def create_barcode_blank(doc, student: Student, schools: list):
    sid = str(student.id)
    st = {'name1': student.name_1, 'name2': student.name_2, 'class_number': student.class_n,
          'class_latter': student.class_l, 'school': schools[student.school_id].short_name, 'id': sid}

    sid = '0' * (7 - len(sid)) + sid
    file_name = Config.WORDS_FOLDER + '/barcode' + sid
    sample_barcode = barcode.get('ean8', sid, writer=ImageWriter())
    sample_barcode.save(file_name)
    file_name += '.png'
    img = Image.open(file_name)
    cropped_img = img.crop((75, 0, 340, 240))
    cropped_img.save(file_name)

    img = InlineImage(doc, file_name, width=Mm(13))
    st['id_barcode'] = img
    return st


@app.route("/<int:iti_id>/create_barcodes")
@cross_origin()
@login_required
@check_status('admin')
@check_block_iti()
def create_barcodes(iti: Iti):
    if not os.path.exists(Config.WORDS_FOLDER):
        os.makedirs(Config.WORDS_FOLDER)
    students = Student.select_by_iti(iti)
    cnt = len(students)
    doc = DocxTemplate(Config.DATA_FOLDER + '/8_barcodes_template.docx')
    schools = {_.id: _ for _ in School.select_all()}
    for i in range(0, cnt, 8):
        context = {'st': []}
        for j in range(i, min(i + 8, cnt)):
            context['st'].append(create_barcode_blank(doc, students[j], schools))
        if cnt < i + 8:
            for j in range(cnt, i + 8):
                context['st'].append(create_empty_barcode_blank())
        doc.render(context)
        doc.save(Config.WORDS_FOLDER + '/bar-{}.docx'.format(i // 8))

    pythoncom.CoInitialize()
    master = Document(Config.WORDS_FOLDER + '/bar-0.docx')
    composer = Composer(master)
    for i in range(8, cnt, 8):
        doc = Document(Config.WORDS_FOLDER + '/bar-{}.docx'.format(i // 8))
        composer.append(doc)
    main_doc = Config.DATA_FOLDER + "/barcodes_{}.docx".format(iti.id)
    composer.save(main_doc)
    convert(main_doc)

    for file in glob(Config.WORDS_FOLDER + '/*.*'):
        os.remove(file)
    return render_template(str(iti.id) + '/codes.html', error='Штрих-коды сгенерированы')


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


@app.route("/<int:iti_id>/save_barcodes", methods=['POST'])
@cross_origin()
@login_required
@check_status('admin')
@check_block_iti()
def save_barcodes(iti: Iti):
    try:
        data = request.form['data']
        value = json.loads(data)
        for line in value:
            student_id = int(line[0])
            if not Student.select(student_id):
                raise ValueError('Школьника "{}" не существует'.format(student_id))
            for barcode in line[1:]:
                if barcode.isdigit():
                    bar = Barcode.select(iti.id, int(barcode))
                    if bar and bar.student_id != student_id:
                        raise ValueError('Штрих-код "{}" уже сохранён на школьника "{}"'.format(barcode, student_id))
        for line in value:
            student_id = line[0]
            for barcode in line[1:]:
                if barcode.isdigit() and not Barcode.select(iti.id, int(barcode)):
                    Barcode.insert(Barcode.build(iti.id, int(barcode), student_id))
    except Exception as ex:
        return jsonify({'status': 'Error', 'msg': str(ex)})
    return jsonify({'status': 'OK'})


@app.route("/<int:iti_id>/upload_barcodes", methods=['POST'])
@cross_origin()
@login_required
@check_status('admin')
@check_block_iti()
def upload_barcodes(iti: Iti):
    file = request.files['file']
    filename = Config.DATA_FOLDER + '/' + str(round(time.time() * 1000)) + '.' + file.filename.rsplit('.')[-1]
    file.save(filename)
    img = Image.open(filename)
    ean8, ean13 = barcodes_from_image(img)

    groups, errors = [], []
    for code in ean8:
        val = [code[0].top, code[0].top + code[0].height, code[1]]
        groups.append(val)
    for code in ean13:
        if len(groups) > 1:
            pos = code[0].top + code[0].height // 2
            for ean8 in groups:
                if ean8[0] <= pos <= ean8[1]:
                    ean8.append(code[1])
                    break
            else:
                errors.append(code)
        elif len(groups) == 1:
            groups[0].append(code[1])
        else:
            errors.append(code)
    groups.sort(key=lambda x: x[0] + x[1])
    new_groups = []
    for group in groups:
        student_id = int(group[2][:-1])
        student = Student.select(student_id)
        student_class = StudentClass.select(iti.id, student_id)
        if not student:
            errors.append(group)
        current = [student.json(), student_class.json(), group[3:]]
        new_groups.append(current)
    os.remove(filename)
    return jsonify({'status': 'OK', 'groups': new_groups, 'errors': errors})


@app.route("/<int:iti_id>/get_codes")
@cross_origin()
@login_required
@check_status('admin')
@check_block_iti()
def get_codes(iti: Iti):
    filename = './data/barcodes_{}.pdf'.format(iti.id)
    return send_file(filename, as_attachment=True, download_name='{}. Бланки для кодировки.pdf'.format(iti.name_in_list))
