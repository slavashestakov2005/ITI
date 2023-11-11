from flask import render_template
from flask_cors import cross_origin
from flask_login import login_required, current_user
from backend import app
from .help import check_status, check_block_iti
from ..database import Message, Iti, School
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
@check_status('admin')
@check_block_iti()
def subjects_for_iti(iti: Iti):
    return render_template(str(iti.id) + '/subjects_for_year.html')


@app.route("/<int:iti_id>/messages_for_year.html")
@cross_origin()
@login_required
@check_status('admin')
@check_block_iti()
def messages_for_iti(iti: Iti):
    return render_template(str(iti.id) + '/messages_for_year.html', messages=Message.select_by_iti(iti.id))


@app.route("/<int:iti_id>/student_edit.html")
@cross_origin()
@login_required
@check_status('admin')
@check_block_iti()
def student_edit(iti: Iti):
    return render_template('student_edit.html', iti=iti)


@app.route("/<int:iti_id>/excel.html")
@cross_origin()
@login_required
@check_status('admin')
@check_block_iti()
def excel_page_for_iti(iti: Iti):
    return render_template('excel.html', iti=iti)


@app.route("/settings.html")
@cross_origin()
@login_required
@check_block_iti()
def settings():
    params = {'password': 'Уже введён' if ConfigMail.MAIL_PASSWORD else 'Отсутствует',
              'email': ConfigMail.MAIL_USERNAME, 'admins': str(ConfigMail.ADMINS)} \
        if current_user.can_do(-2) else {}
    return render_template('settings.html', **params)


@app.route("/<int:iti_id>/rating_students_check.html")
@cross_origin()
@login_required
@check_status('admin')
@check_block_iti()
def rating_students_check(iti: Iti):
    return render_template(str(iti.id) + '/rating_students_check.html')


@app.route("/school_edit.html")
@cross_origin()
@login_required
@check_status('admin')
def school_edit():
    return render_template('school_edit.html', schools=School.select_all())


@app.route("/<int:iti_id>/codes.html")
@cross_origin()
@login_required
@check_status('admin')
@check_block_iti()
def iti_codes_page(iti: Iti):
    return render_template('codes.html', iti=iti)


@app.route("/<int:iti_id>/barcodes_edit.html")
@cross_origin()
@login_required
@check_status('admin')
@check_block_iti()
def iti_barcodes_edit_page(iti: Iti):
    return render_template('barcodes_edit.html', iti=iti)
