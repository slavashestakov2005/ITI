from backend import app
from .. import Config
from ..database import Student, Iti, School
from .help import check_status, check_block_iti
from flask import render_template, send_file, request, jsonify
from flask_cors import cross_origin
from flask_login import login_required

from glob import glob
import os
from PIL import Image
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
from docx import Document
from docxcompose.composer import Composer
import barcode
from barcode.writer import ImageWriter
'''
    /<iti_id>/create_barcodes               Создаёт PDF-документ с штрих-кодами участников (admin).
    /<iti_id>/get_codes                     Возвращает PDF-документ с бланками участников (admin).
'''


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

    for file in glob(Config.WORDS_FOLDER + '/*.*'):
        os.remove(file)
    return render_template(str(iti.id) + '/codes.html', error='Штрих-коды сгенерированы')


@app.route("/<int:iti_id>/get_codes")
@cross_origin()
@login_required
@check_status('admin')
@check_block_iti()
def get_codes(iti: Iti):
    filename = './data/barcodes_{}.docx'.format(iti.id)
    return send_file(filename, as_attachment=True, download_name='{}. Бланки для кодировки.docx'.format(iti.name_in_list))
