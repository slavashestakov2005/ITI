from backend import app
from flask import render_template, request, redirect
from flask_cors import cross_origin
from flask_login import current_user, login_required
from backend.database import UsersTable, User
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


@app.route("/settings", methods=['GET', 'POST'])
@cross_origin()
@login_required
@check_block_year()
def settings():
    if request.method == 'POST':
        try:
            password_old = request.form['password_old']
            password = request.form['password']
            password2 = request.form['password2']
            empty_checker(password_old, password, password2)
        except Exception:
            return render_template(TEMPLATE1, error='Некорректные данные')

        if current_user.check_password(password_old):
            if password == password2:
                current_user.set_password(password)
                UsersTable.update_by_login(current_user)
                return render_template(TEMPLATE1, error='Ваш пароль обнавлён')
            else:
                return render_template(TEMPLATE1, error='Новые пароли {0} и {1} не совпадают'.format(password, password2))
        else:
            return render_template(TEMPLATE1, error='Ваш старый пароль не {0}'.format(password_old))
    params = {'password': 'Уже введён' if ConfigMail.MAIL_PASSWORD else 'Отсутствует',
              'email': ConfigMail.MAIL_USERNAME, 'admins': str(ConfigMail.ADMINS)} \
        if current_user.can_do(-2) else {}
    return render_template(TEMPLATE1, **params)


@app.route("/registration", methods=['GET', 'POST'])
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def registration():
    if request.method == 'POST':
        try:
            user_login = request.form['login']
            user_password = request.form['password']
            user_password2 = request.form['password2']
            user_status = request.form.getlist('status')
            empty_checker(user_login, user_password, user_password2)
        except Exception:
            return render_template(TEMPLATE2, error1='Некорректные данные')

        u = UsersTable.select_by_login(user_login)
        if u.__is_none__:
            if user_password == user_password2:
                u = User([None, user_login, '', -100, ''])
                u.set_password(user_password)
                u.set_status(user_status)
                UsersTable.insert(u)
                Generator.gen_users_list()
                return render_template(TEMPLATE2, error1='Пользователь {0} зарегистрирован'.format(user_login))
            else:
                return render_template(TEMPLATE2, error1='Пароли {0} и {1} не совпадают'.
                                       format(user_password, user_password2), login1=user_login)
        else:
            return render_template(TEMPLATE2, error1='Пользователь {0} уже существует'.format(user_login))
    return redirect('user_edit.html')


@app.route("/edit_status", methods=['GET', 'POST'])
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def edit_status():
    if request.method == 'POST':
        try:
            user_login = request.form['login']
            user_status = request.form.getlist('status')
            empty_checker(user_login)
        except Exception:
            return render_template(TEMPLATE2, error2='Некорректные данные')

        u = UsersTable.select_by_login(user_login)
        if not u.__is_none__:
            u.set_status(user_status)
            UsersTable.update_by_login(u)
            Generator.gen_users_list()
            return render_template(TEMPLATE2, error2='Статус пользователя {0} обнавлён'.format(user_login))
        else:
            return render_template(TEMPLATE2, error2='Пользователя {0} не существует'.format(user_login))
    return redirect('user_edit.html')


@app.route("/delete", methods=['GET', 'POST'])
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def delete():
    if request.method == 'POST':
        try:
            user_login = request.form['login']
            empty_checker(user_login)
        except Exception:
            return render_template(TEMPLATE2, error3='Некорректные данные')

        u = UsersTable.select_by_login(user_login)
        if not u.__is_none__:
            UsersTable.delete(u)
            Generator.gen_users_list()
            return render_template(TEMPLATE2, error3='Пользователь {0} удалён'.format(user_login))
        else:
            return render_template(TEMPLATE2, error3='Пользователя {0} не существует'.format(user_login))
    return redirect('user_edit.html')
