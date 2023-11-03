from backend import app
from ..database import Student, Iti, School, Code
from .help import check_status, check_block_iti
from flask import render_template, send_file
from flask_cors import cross_origin
from flask_login import login_required
from ..help import FileNames
from ..excel import ExcelCodesWriter
from random import shuffle
from ..config import Config

'''
    /<iti_id>/create_codes                  Создаёт EXCEL-документ с кодами участников (admin).
    /<iti_id>/get_codes                     Возвращает EXCEL-документ с кодами участников (admin).
'''


@app.route("/<int:iti_id>/create_codes")
@cross_origin()
@login_required
@check_status('admin')
@check_block_iti()
def create_codes(iti: Iti):
    Code.delete_by_iti(iti.id)
    students = sorted(Student.select_by_iti(iti), key=Student.sort_by_all)
    codes = [code for code in range(1000, 10000)]
    shuffle(codes)
    data = []
    schools = School.select_id_dict()
    for student, code in zip(students, codes):
        Code.insert(Code.build(iti.id, student.id, code))
        data.append([student.name_1, student.name_2, student.name_3, student.school_name(schools), student.class_name(),
                     code])
    store_name, send_name = FileNames.codes_excel(iti)
    ExcelCodesWriter().write(Config.DATA_FOLDER + '/' + store_name, data)
    return render_template('codes.html', iti=iti, error='Кодировка сгенерирована')


@app.route("/<int:iti_id>/get_codes")
@cross_origin()
@login_required
@check_status('admin')
@check_block_iti()
def get_codes(iti: Iti):
    store_name, send_name = FileNames.codes_excel(iti)
    filename = './data/' + store_name
    return send_file(filename, as_attachment=True, download_name=send_name)
