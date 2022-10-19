from backend import app, login
from flask import render_template, request, redirect
from flask_cors import cross_origin
from flask_login import login_user, logout_user, current_user
from backend.database import UsersTable
from backend.queries.help import check_block_year, empty_checker
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
    return UsersTable.select(int(id))


@app.route("/login", methods=['GET', 'POST'])
@cross_origin()
@check_block_year()
def login():
    if current_user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        try:
            user_login = request.form['login']
            user_password = request.form['password']
            empty_checker(user_login, user_password)
        except Exception:
            return render_template(TEMPLATE, error='Некорректные данные')

        u = UsersTable.select_by_login(user_login)
        if not u.__is_none__ and u.check_password(user_password):
            login_user(u)
            return redirect('/')
        else:
            return render_template(TEMPLATE, error='Пользователя с логином {0} и паролем {1} не существует'
                                   .format(user_login, user_password))
    return render_template(TEMPLATE)


@app.route("/eljur_login", methods=['POST'])
@cross_origin()
@check_block_year()
def eljur_login():
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
@check_block_year()
def logout():
    logout_user()
    return render_template('index.html')
