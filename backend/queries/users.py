from backend import app, login
from flask import render_template, request, redirect
from flask_cors import cross_origin
from flask_login import login_user, logout_user, current_user, login_required
from backend.database import UsersTable, User
from .help import check_status

'''
    /login          login()             Вход пользователя.
    /logout         logout()            Выход пользователя.
    /settings       settings()          Изменение данных текущего пользователя.
    /registration   registration()      Регистрирует пользователя (только для admin).
    /edit_status    edit_status()       Редактирует статус другого пользователя (только для admin).
    /delete         delete()            Удаляет другого пользователя.
'''


@login.user_loader
def load_user(id):
    return UsersTable.select_by_id(int(id))


@app.route("/login", methods=['GET', 'POST'])
@cross_origin()
def login():
    if current_user.is_authenticated:
        return redirect('index.html')
    if request.method == 'POST':
        user_login = request.form['login']
        user_password = request.form['password']
        u = UsersTable.select_by_login(user_login)
        if not u.__is_none__ and u.check_password(user_password):
            login_user(u)
            return redirect('index.html')
        else:
            return render_template('login.html', error='Пользователя с логином ' + user_login + ' и паролем ' +
                                                       user_password + ' не существует')
    return render_template('login.html')


@app.route("/logout")
@cross_origin()
def logout():
    logout_user()
    return render_template('index.html')


@app.route("/settings", methods=['GET', 'POST'])
@cross_origin()
@login_required
def settings():
    if request.method == 'POST':
        password_old = request.form['password_old']
        password = request.form['password']
        password2 = request.form['password2']
        if current_user.check_password(password_old):
            if password == password2:
                current_user.set_password(password)
                UsersTable.update_by_login(current_user)
                return render_template('settings.html', error='Ваш пароль обнавлён')
            else:
                return render_template('settings.html', error='Новые пароли ' + password + ' и ' + password2 +
                                                              ' не совпадают')
        else:
            return render_template('settings.html', error='Ваш старый пароль не ' + password_old)
    params = {'password': 'Уже введён' if app.config['MAIL_PASSWORD'] else 'Отсутствует',
              'email': app.config['MAIL_USERNAME'], 'admins': str(app.config['ADMINS'])}\
        if current_user.can_do(-2) else {}
    return render_template('settings.html', **params)


@app.route("/registration", methods=['GET', 'POST'])
@cross_origin()
@login_required
@check_status('admin')
def registration():
    if request.method == 'POST':
        user_login = request.form['login']
        user_password = request.form['password']
        user_password2 = request.form['password2']
        user_status = request.form.getlist('status')
        u = UsersTable.select_by_login(user_login)
        if u.__is_none__:
            if user_password == user_password2:
                u = User([None, user_login, '', -100])
                u.set_password(user_password)
                u.set_status(user_status)
                UsersTable.insert(u)
                return render_template('user_edit.html', error1='Пользователь ' + user_login + ' зарегистрирован')
            else:
                return render_template('user_edit.html', error1='Пароли ' + user_password + ' и ' + user_password2 +
                                                                ' не совпадают', login1=user_login)
        else:
            return render_template('user_edit.html', error1='Пользователь ' + user_login + ' уже существует')
    return redirect('user_edit.html')


@app.route("/edit_status", methods=['GET', 'POST'])
@cross_origin()
@login_required
@check_status('admin')
def edit_status():
    if request.method == 'POST':
        user_login = request.form['login']
        user_status = request.form.getlist('status')
        u = UsersTable.select_by_login(user_login)
        if not u.__is_none__:
            u.set_status(user_status)
            UsersTable.update_by_login(u)
            return render_template('user_edit.html', error2='Статус пользователя ' + user_login + ' обнавлён')
        else:
            return render_template('user_edit.html', error2='Пользователя ' + user_login + ' не существует')
    return redirect('user_edit.html')


@app.route("/delete", methods=['GET', 'POST'])
@cross_origin()
@login_required
@check_status('admin')
def delete():
    if request.method == 'POST':
        user_login = request.form['login']
        u = UsersTable.select_by_login(user_login)
        if not u.__is_none__:
            UsersTable.delete(u)
            return render_template('user_edit.html', error3='Пользователь ' + user_login + ' удалён')
        else:
            return render_template('user_edit.html', error3='Пользователя ' + user_login + ' не существует')
    return redirect('user_edit.html')
