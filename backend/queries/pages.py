from flask import render_template
from flask_cors import cross_origin
from flask_login import current_user, login_required

from backend import app
from .help import check_access
from ..database import Barcode, Iti, ItiSubject, Message, Result, School, Student, Subject
from ..help import ConfigMail

'''
    /<iti_id>/subjects_for_year.html        Возвращает страницу с настройками ИТИ (admin).
    /<iti_id>/messages_for_year.html        Возвращает страницу с новостями ИТИ (admin).
    /<iti_id>/student_edit.html             Возвращает страницу со списком школьников (admin).
    /<iti_id>/excel.html                    Возвращает страницу со списком Excel таблиц (admin).
    /settings.html                          Возвращает страницу с настройками пользователя.
    /<iti_id>/rating_students_check.html    Возвращает страницу для простановки галочек на участие в командах (admin).
    /school_edit.html                       Возвращает страницу с настройками школ (admin).
    /<iti_id>/codes.html                    Возвращает страницу с данными о кодировке школьников (admin).
    /<iti_id>/barcodes_edit.html            Возвращает страницу для редактирования информации штрих-код -- школьник (admin).
'''


@app.route("/<int:iti_id>/subjects_for_year.html")
@cross_origin()
@login_required
@check_access(status='admin', block=True)
def subjects_for_iti(iti: Iti):
    return render_template(str(iti.id) + '/subjects_for_year.html')


@app.route("/<int:iti_id>/messages_for_year.html")
@cross_origin()
@login_required
@check_access(status='admin', block=True)
def messages_for_iti(iti: Iti):
    return render_template(str(iti.id) + '/messages_for_year.html', messages=Message.select_by_iti(iti.id))


@app.route("/<int:iti_id>/student_edit.html")
@cross_origin()
@login_required
@check_access(status='admin', block=True)
def student_edit(iti: Iti):
    return render_template('student_edit.html', iti=iti)


@app.route("/<int:iti_id>/excel.html")
@cross_origin()
@login_required
@check_access(status='admin', block=True)
def excel_page_for_iti(iti: Iti):
    return render_template('excel.html', iti=iti)


@app.route("/settings.html")
@cross_origin()
@login_required
@check_access(block=True)
def settings():
    params = {'password': 'Уже введён' if ConfigMail.MAIL_PASSWORD else 'Отсутствует',
              'email': ConfigMail.MAIL_USERNAME, 'admins': str(ConfigMail.ADMINS)} \
        if current_user.can_do(-2) else {}
    return render_template('settings.html', **params)


@app.route("/<int:iti_id>/rating_students_check.html")
@cross_origin()
@login_required
@check_access(status='admin', block=True)
def rating_students_check(iti: Iti):
    return render_template(str(iti.id) + '/rating_students_check.html')


@app.route("/<int:iti_id>/rating.html")
@cross_origin()
@check_access()
def rating(iti: Iti):
    return render_template(str(iti.id) + '/rating.html', iti_id=iti.id, super_is_open=iti.super_is_open)


@app.route("/school_edit.html")
@cross_origin()
@login_required
@check_access(status='admin')
def school_edit():
    return render_template('school_edit.html', schools=School.select_all())


@app.route("/<int:iti_id>/codes.html")
@cross_origin()
@login_required
@check_access(status='admin', block=True)
def iti_codes_page(iti: Iti):
    return render_template('codes.html', iti=iti)


@app.route("/<int:iti_id>/barcodes_edit.html")
@cross_origin()
@login_required
@check_access(status='admin', block=True)
def iti_barcodes_edit_page(iti: Iti):
    all_subjects = Subject.select_id_dict()
    iti_subjects = ItiSubject.select_by_iti(iti.id)
    subjects = {item.id: all_subjects[item.subject_id] for item in iti_subjects}
    barcodes_list = Barcode.select_by_iti(iti.id)
    results_list = []
    for ys in iti_subjects:
        results_list.extend(Result.select_by_iti_subject(ys.id))
    barcodes_dict = {item.code: item for item in barcodes_list}
    results_dict = {item.student_code: item for item in results_list}
    students = {_.id: _ for _ in Student.select_by_iti(iti)}
    schools = School.select_id_dict()
    return render_template('barcodes_edit.html', iti=iti, students=students, schools=schools, subjects=subjects,
                           barcodes_list=barcodes_list, barcodes_dict=barcodes_dict, results_list=results_list,
                           results_dict=results_dict)
