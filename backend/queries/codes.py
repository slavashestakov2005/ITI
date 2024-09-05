from flask import render_template, request, send_file
from flask_cors import cross_origin
from flask_login import login_required
from random import shuffle

from backend import app
from .help import check_access
from ..config import Config
from ..database import Code, Iti, School, Student
from ..excel import ExcelCodesWriter
from ..help import FileNames, UserRoleIti

'''
    /<iti_id>/create_codes                  Создаёт EXCEL-документ с кодами участников (admin).
    /<iti_id>/get_codes                     Возвращает EXCEL-документ с кодами участников (admin).
'''


@app.route("/<int:iti_id>/create_codes")
@cross_origin()
@login_required
@check_access(roles=[UserRoleIti.ADMIN], block=True)
def create_codes(iti: Iti):
    only_new = request.args.get('new') == '1'
    codes = {code for code in range(1000, 10000)}
    if only_new:
        Code.delete_by_iti(iti.id)
        students = Student.select_by_iti(iti)
    else:
        have_codes = Code.select_by_iti(iti.id)
        students_with_codes = {code.student_id for code in have_codes}
        students = [student for student in Student.select_by_iti(iti) if student.id not in students_with_codes]
        codes -= {code.code for code in have_codes}
    students = sorted(students, key=Student.sort_by_all)
    codes = list(codes)
    shuffle(codes)
    schools = School.select_id_dict()
    for student, code in zip(students, codes):
        Code.insert(Code.build(iti.id, student.id, code))
    data = []
    for stud in sorted(Student.select_by_iti(iti), key=Student.sort_by_all):
        code = Code.select_by_student(iti.id, stud.id)
        data.append([stud.name_1, stud.name_2, stud.name_3, stud.school_name(schools), stud.class_name(), code.code])
    store_name, send_name = FileNames.codes_excel(iti)
    ExcelCodesWriter().write(Config.DATA_FOLDER + '/' + store_name, data)
    return render_template('codes.html', iti=iti, error='Кодировка сгенерирована')


@app.route("/<int:iti_id>/get_codes")
@cross_origin()
@login_required
@check_access(roles=[UserRoleIti.ADMIN], block=True)
def get_codes(iti: Iti):
    store_name, send_name = FileNames.codes_excel(iti)
    filename = './data/' + store_name
    return send_file(filename, as_attachment=True, download_name=send_name)
