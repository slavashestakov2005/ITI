from flask import render_template
from flask_cors import cross_origin
from flask_login import login_required, current_user
from backend import app
from .help import check_status, check_block_year
from ..database import Message, Year
from ..help import ConfigMail
'''
    /<year>/subjects_for_year.html          Возвращает страницу с настройками года (admin).
    /<year>/messages_for_year.html          Возвращает страницу с объявлениями года (admin).
    /<year>/student_edit.html               Возвращает страницу со списком школьников (admin).
    /<year>/excel.html                      Возвращает страницу со списком Excel таблиц (admin).
    /settings.html                          Возвращает страницу с настройками пользователя.
'''


@app.route("/<year:year>/subjects_for_year.html")
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def subjects_for_year(year: int):
    return render_template(str(year) + '/subjects_for_year.html', year=abs(year))


@app.route("/<year:year>/messages_for_year.html")
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def messages_for_year(year: int):
    return render_template(str(year) + '/messages_for_year.html', messages=Message.select_by_year(year))


@app.route("/<year:year>/student_edit.html")
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def student_edit(year: int):
    year_info = Year.select(year)
    if year_info is None:
        return render_template('student_edit.html', year=year, year_info=year_info)
    return render_template('student_edit.html', year=year, year_info=year_info)


@app.route("/<year:year>/excel.html")
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def excel_page_for_year(year: int):
    return render_template('excel.html', year=year)


@app.route("/settings.html")
@cross_origin()
@login_required
@check_block_year()
def settings():
    params = {'password': 'Уже введён' if ConfigMail.MAIL_PASSWORD else 'Отсутствует',
              'email': ConfigMail.MAIL_USERNAME, 'admins': str(ConfigMail.ADMINS)} \
        if current_user.can_do(-2) else {}
    return render_template('settings.html', **params)
