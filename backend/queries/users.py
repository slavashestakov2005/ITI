from backend import app
from flask import render_template, request, redirect
from flask_cors import cross_origin
from flask_login import current_user, login_required
from ..database import User
from .help import check_status, check_block_year, empty_checker
from ..help import ConfigMail
from .auto_generator import Generator
'''
                    TEMPLATE1           Имя шаблона с настройкой пользователя (себя).
                    TEMPLATE2           Имя шаблона с настройкой другого пользователя.
    /settings       settings()          Изменение данных текущего пользователя.
    /registration   registration()      Регистрирует пользователя (только для admin).
    /edit_status    edit_status()       Редактирует статус другого пользователя (только для admin).
    /delete         delete()            Удаляет другого пользователя.
'''


TEMPLATE1, TEMPLATE2 = 'settings.html', 'user_edit.html'


@app.route("/settings")
@cross_origin()
@login_required
@check_block_year()
def settings():
    params = {'password': 'Уже введён' if ConfigMail.MAIL_PASSWORD else 'Отсутствует',
              'email': ConfigMail.MAIL_USERNAME, 'admins': str(ConfigMail.ADMINS)} \
        if current_user.can_do(-2) else {}
    return render_template(TEMPLATE1, **params)


@app.route("/registration")
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def registration():
    return redirect('user_edit.html')


@app.route("/edit_status")
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def edit_status():
    return redirect('user_edit.html')


@app.route("/delete")
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def delete():
    return redirect('user_edit.html')
