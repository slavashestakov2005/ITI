from flask import redirect, render_template, request
from flask_cors import cross_origin
from flask_login import current_user, login_user, logout_user

from backend import app, login
from backend.queries.help import empty_checker
from ..database import User
from ..eljur import EljurUser

'''
                    TEMPLATE            Страница входа.
    /login          login()             Вход пользователя.
    /eljur_login    eljur_login()       Вход через Eljur.
    /logout         logout()            Выход пользователя.
'''


TEMPLATE, ELJUR_LOGIN = 'login.html', 'eljur_login.html'


@login.user_loader
def load_user(id):
    return User.select(int(id))


@app.route("/login", methods=['GET', 'POST'])
@cross_origin()
def login():
    if current_user.is_authenticated:
        return redirect('/admin_panel')
    if request.method == 'POST':
        try:
            user_login = request.form['login']
            user_password = request.form['password']
            empty_checker(user_login, user_password)
        except Exception:
            return render_template(TEMPLATE, error='Некорректные данные')

        u = User.select_by_login(user_login)
        if u is not None and u.check_password(user_password):
            login_user(u)
            return redirect('/')
        else:
            return render_template(TEMPLATE, error='Неверные логин или пароль')
    return render_template(TEMPLATE)


@app.route("/eljur_login", methods=['GET', 'POST'])
@cross_origin()
def eljur_login():
    if request.method == 'GET':
        return render_template(ELJUR_LOGIN)
    try:
        user_login = request.form['login']
        user_password = request.form['password']
        empty_checker(user_login, user_password)
    except Exception:
        return render_template(ELJUR_LOGIN, error='Некорректные данные')

    x = EljurUser.login(user_login, user_password)
    if not x:
        return render_template(ELJUR_LOGIN, error='Некорректные данные')
    return x


@app.route("/logout")
@cross_origin()
def logout():
    logout_user()
    return redirect('/')
