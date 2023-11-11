from backend import app
from .. import Config
from ..database import Student, Iti, School
from ..excel import ExcelBarcodesWriter
from .help import check_status, check_block_iti
from flask import render_template, send_file, request
from flask_cors import cross_origin
from flask_login import login_required

from glob import glob
import os
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
from docx import Document
from docxcompose.composer import Composer
import barcode
from barcode.writer import ImageWriter

from ..help import FileNames

'''
    /<iti_id>/create_barcodes               Создаёт WORD-документ с штрих-кодами участников (admin).
    /<iti_id>/get_barcodes                  Возвращает WORD-документ с бланками участников (admin).
    /<iti_id>/get_excel_with_barcodes       Возвращает EXCEL-документ со штрих-кодами из заданного диапазона (admin).
'''


def create_empty_barcode_blank():
    return {}


def create_barcode_blank(doc, student: Student, schools: dict):
    sid = str(student.id)
    st = {'name1': student.name_1, 'name2': student.name_2, 'class_number': student.class_n,
          'class_latter': student.class_l, 'school': schools[student.school_id].short_name, 'id': sid}

    sid = '0' * (7 - len(sid)) + sid
    file_name = Config.WORDS_FOLDER + '/barcode' + sid
    sample_barcode = barcode.get('ean8', sid, writer=ImageWriter())
    sample_barcode.save(file_name)
    file_name += '.png'
    img = InlineImage(doc, file_name, width=Mm(40))
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
    students = sorted(Student.select_by_iti(iti), key=Student.sort_by_all)
    cnt = len(students)
    barcodes_on_page = 6
    doc = DocxTemplate(Config.DATA_FOLDER + '/{}_barcodes_template.docx'.format(barcodes_on_page))
    schools = School.select_id_dict()
    for i in range(0, cnt, barcodes_on_page):
        context = {'st': []}
        for j in range(i, min(i + barcodes_on_page, cnt)):
            context['st'].append(create_barcode_blank(doc, students[j], schools))
        if cnt < i + barcodes_on_page:
            for j in range(cnt, i + barcodes_on_page):
                context['st'].append(create_empty_barcode_blank())
        doc.render(context)
        doc.save(Config.WORDS_FOLDER + '/bar-{}.docx'.format(i // barcodes_on_page))
    master = Document(Config.WORDS_FOLDER + '/bar-0.docx')
    composer = Composer(master)
    for i in range(barcodes_on_page, cnt, barcodes_on_page):
        doc = Document(Config.WORDS_FOLDER + '/bar-{}.docx'.format(i // barcodes_on_page))
        composer.append(doc)
    store_name, send_name = FileNames.barcodes_word(iti)
    main_doc = Config.DATA_FOLDER + "/" + store_name
    composer.save(main_doc)
    for file in glob(Config.WORDS_FOLDER + '/*.*'):
        os.remove(file)
    return render_template('codes.html', error='Документ с листочками сгенерирован', iti=iti)


@app.route("/<int:iti_id>/get_barcodes")
@cross_origin()
@login_required
@check_status('admin')
@check_block_iti()
def get_barcodes(iti: Iti):
    store_name, send_name = FileNames.barcodes_word(iti)
    filename = './data/' + store_name
    return send_file(filename, as_attachment=True, download_name=send_name)


@app.route("/<int:iti_id>/get_excel_with_barcodes", methods=['POST'])
@cross_origin()
@login_required
@check_status('admin')
@check_block_iti()
def get_excel_with_barcodes(iti: Iti):
    MOD = 10 ** 12
    try:
        add_checksum = 'add_checksum' in request.form
        start_barcode = int(request.form['start_barcode']) % MOD
        end_barcode = int(request.form['end_barcode']) % MOD
    except Exception:
        return render_template('codes.html', error='Не переданы начальные и конечные коды')
    store_name, send_name = FileNames.barcodes_excel(iti, start_barcode, end_barcode)
    data = []
    for code in range(start_barcode, end_barcode + 1):
        bar = '0' * (12 - len(str(code))) + str(code)
        if add_checksum:
            full_bar = str(barcode.get('ean13', bar))
        else:
            full_bar = bar
        data.append([full_bar])
        data.append([full_bar])
    ExcelBarcodesWriter().write(Config.DATA_FOLDER + '/' + store_name, data)
    filename = './data/' + store_name
    return send_file(filename, as_attachment=True, download_name=send_name)
