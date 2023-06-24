from flask import render_template
from flask_cors import cross_origin
from flask_login import login_required, current_user
from backend import app
from .help import check_status, check_block_year
from ..database import Message
from ..help import ConfigMail
'''
    /<year>/subjects_for_year.html          Возвращает страницу с настройками года (admin).
    /settings.html                          Возвращает страницу с настройками пользователя.
'''


@app.route("/<year:year>/subjects_for_year.html")
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def subjects_for_year(year: int):
    return render_template(str(year) + '/subjects_for_year.html', year=abs(year), messages=Message.select_by_year(year))


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
