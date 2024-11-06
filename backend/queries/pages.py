from flask import render_template
from flask_cors import cross_origin

from backend import app
from .help import check_access, route_iti_html_page
from ..database import Barcode, Iti, ItiSubject, Message, Result, School, Student, Subject
from ..help import check_role, ConfigMail, not_found_error, UserRoleGlobal, UserRoleIti, UserRoleLogin

'''
    /<iti_id>/subjects_for_year             Возвращает страницу с настройками ИТИ (admin).
    /<iti_id>/messages_for_year             Возвращает страницу с новостями ИТИ (admin).
    /<iti_id>/student_edit                  Возвращает страницу со списком школьников (admin).
    /<iti_id>/excel                         Возвращает страницу со списком Excel таблиц (admin).
    /settings                               Возвращает страницу с настройками пользователя.
    /<iti_id>/rating_students_check         Возвращает страницу для простановки галочек на участие в командах (admin).
    /school_edit                            Возвращает страницу с настройками школ (admin).
    /<iti_id>/codes                         Возвращает страницу с данными о кодировке школьников (admin).
    /<iti_id>/barcodes_edit                 Возвращает страницу для редактирования информации штрих-код -- школьник (admin).
'''


@app.route("/<int:iti_id>/subjects_for_year")
@cross_origin()
@route_iti_html_page(page='subjects_for_year', roles=[UserRoleIti.ADMIN], block=True)
def iti_subjects_for_year_page(iti: Iti):
    return {}


@app.route("/<int:iti_id>/messages_for_year")
@cross_origin()
@route_iti_html_page(page='messages_for_year', roles=[UserRoleIti.ADMIN], block=True)
def iti_messages__for_year_page(iti: Iti):
    return {'messages': Message.select_by_iti(iti.id)}


@app.route("/<int:iti_id>/student_edit")
@cross_origin()
@route_iti_html_page(page='student_edit.html', roles=[UserRoleIti.ADMIN], block=True, root=True)
def iti_student_edit_page(iti: Iti):
    return {}


@app.route("/<int:iti_id>/excel")
@cross_origin()
@route_iti_html_page(page='excel.html', roles=[UserRoleIti.ADMIN], block=True, root=True)
def iti_excel_page(iti: Iti):
    return {}


@app.route("/settings")
@cross_origin()
@check_access(roles=[UserRoleLogin.LOGIN_LOCAL], block=False)
def settings():
    params = {'password': 'Уже введён' if ConfigMail.MAIL_PASSWORD else 'Отсутствует',
              'email': ConfigMail.MAIL_USERNAME, 'admins': str(ConfigMail.ADMINS)} \
        if check_role(roles=[UserRoleGlobal.FULL]) else {}
    return render_template('settings.html', **params)


@app.route("/<int:iti_id>/rating")
@cross_origin()
@route_iti_html_page(page='rating', block=False)
def iti_rating_page(iti: Iti):
    return {}


@app.route("/<int:iti_id>/rating_students")
@cross_origin()
@route_iti_html_page(page='rating_students', block=False)
def iti_rating_students_page(iti: Iti):
    return {}


@app.route("/<int:iti_id>/rating_students_check")
@cross_origin()
@route_iti_html_page(page='rating_students_check', roles=[UserRoleIti.ADMIN], block=True)
def iti_rating_students_check_page(iti: Iti):
    return {}


@app.route("/<int:iti_id>/rating_classes")
@cross_origin()
@route_iti_html_page(page='rating_classes', block=False)
def iti_rating_classes_page(iti: Iti):
    return {}


@app.route("/<int:iti_id>/rating_teams")
@cross_origin()
@route_iti_html_page(page='rating_teams', block=False)
def iti_rating_teams_page(iti: Iti):
    return {}


@app.route("/school_edit")
@cross_origin()
@check_access(roles=[UserRoleGlobal.CHANGE_SCHOOL], block=False)
def school_edit():
    return render_template('school_edit.html', schools=School.select_all())


@app.route("/<int:iti_id>/codes")
@cross_origin()
@route_iti_html_page(page='codes.html', roles=[UserRoleIti.ADMIN], block=True, root=True)
def iti_codes_page(iti: Iti):
    return {}


@app.route("/<int:iti_id>/barcodes_edit")
@cross_origin()
@check_access(roles=[UserRoleIti.ADMIN], block=True)
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


@app.route("/<int:iti_id>/roles_edit")
@cross_origin()
@route_iti_html_page(page='roles_edit', roles=[UserRoleGlobal.CHANGE_USER], block=True)
def roles_edit_page(iti: Iti):
    return {}


@app.route("/<int:iti_id>/timetable")
@cross_origin()
@route_iti_html_page(page='timetable', block=False)
def timetable_page(iti: Iti):
    return {}


@app.route("/<int:iti_id>/students_<int:class_n>")
@cross_origin()
@check_access(roles=[UserRoleIti.ADMIN], block=False)
def iti_students_classn_page(iti: Iti, class_n: int):
    return render_template('{}/students_{}.html'.format(iti.id, class_n), iti=iti)


@app.route("/subjects_edit")
@cross_origin()
@check_access(roles=[UserRoleGlobal.CHANGE_SUBJECT], block=False)
def subjects_edit_page():
    return render_template('subjects_edit.html')


@app.route("/upload_excel")
@cross_origin()
@check_access(roles=[UserRoleGlobal.FULL], block=False)
def upload_excel_page():
    return render_template('upload_excel.html')


@app.route("/user_edit")
@cross_origin()
@check_access(roles=[UserRoleGlobal.CHANGE_USER], block=False)
def user_edit_page():
    return render_template('user_edit.html')


@app.route("/years_edit")
@cross_origin()
@check_access(roles=[UserRoleGlobal.CHANGE_ITI], block=False)
def years_edit_page():
    return render_template('years_edit.html')


@app.route("/<int:iti_id>/<int:subject_id>")
@cross_origin()
@check_access(block=False)
def iti_subject_page(iti: Iti, subject_id: int):
    try:
        subject = Subject.select(subject_id)
        if subject is None:
            raise ValueError()
        ys = ItiSubject.select(iti.id, subject_id)
        if ys is None:
            raise ValueError()
    except Exception:
        return not_found_error()
    return render_template('{}/{}.html'.format(iti.id, subject.id), iti=iti)
