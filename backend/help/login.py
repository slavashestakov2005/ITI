from datetime import datetime
from flask import redirect, render_template, request
from flask_cors import cross_origin
from flask_login import current_user, login_user, logout_user

from backend import app, login
from backend.queries.help import empty_checker, split_class
from ..database import get_student_by_params, Student, StudentEljur, TgUser, User
from ..eljur import ConfigEljur, EljurHelp, EljurLoginByOauth, EljurLoginByPassword

'''
                    TEMPLATE            Страница входа.
    /login          login()             Вход пользователя.
    /eljur_login    eljur_login()       Вход через Eljur.
    /logout         logout()            Выход пользователя.
'''


TEMPLATE, ELJUR_LOGIN = 'login.html', 'eljur_login.html'


# id < 0 - User; id > 0 - Student
@login.user_loader
def load_user(id):
    id = int(id)
    if id < 0:
        return User.select(-id)
    else:
        return Student.select(id)


@app.route("/login", methods=['GET', 'POST'])
@cross_origin()
def login():
    args = {'oauth_eljur_page': ConfigEljur.OAUTH_ELJUR_PAGE}
    from .roles import check_role, UserRoleLogin
    if current_user.is_authenticated and check_role(user=current_user, roles=[UserRoleLogin.LOGIN_LOCAL]):
        return redirect('/admin_panel')
    if current_user.is_authenticated and check_role(user=current_user, roles=[UserRoleLogin.LOGIN_ELJUR]):
        return redirect('/eljur_panel')
    if request.method == 'POST':
        try:
            user_login = request.form['login']
            user_password = request.form['password']
            empty_checker(user_login, user_password)
        except Exception:
            return render_template(TEMPLATE, error='Некорректные данные', **args)

        u = User.select_by_login(user_login)
        if u is not None and u.check_password(user_password):
            u.id = -u.id
            login_user(u)
            return redirect('/')
        else:
            return render_template(TEMPLATE, error='Неверные логин или пароль', **args)
    return render_template(TEMPLATE, **args)


def update_info_for_bot(tg: int, eljur_data: dict) -> None:
    bot_user = TgUser.select(tg)
    new_info = TgUser.build(tg, eljur_data['eljur_id'], datetime.now(), eljur_data['role'])
    if bot_user is None:
        TgUser.insert(new_info)
    else:
        bot_user ^= new_info
        TgUser.update(bot_user)


def eljur_login_raw(eljur_answer: dict, tg: int=None):
    args = {'oauth_eljur_page': ConfigEljur.OAUTH_ELJUR_PAGE}
    if not eljur_answer:
        return render_template(ELJUR_LOGIN, error='Некорректные данные', **args)
    eljur_data = EljurHelp.parse_data(eljur_answer)
    if eljur_data['role'] != 'student':
        return render_template(ELJUR_LOGIN, error='Зайти через Eljur пока могут только школьники', **args)
    se = StudentEljur.select_by_eljur(eljur_data['eljur_id'])
    if se is not None:
        student = Student.select(se.student_id)
        if student is not None:
            if tg is not None:
                update_info_for_bot(tg, eljur_data)
            login_user(student)
            return redirect('/')
        return render_template(ELJUR_LOGIN, error='Школьник не найден', **args)
    cls_n, cls_l = split_class(eljur_data['class'])
    student = get_student_by_params(8, eljur_data['name1'], eljur_data['name2'], cls_n, cls_l)
    if student is not None:
        StudentEljur.insert(StudentEljur.build(student.id, eljur_data['eljur_id']))
        if tg is not None:
            update_info_for_bot(tg, eljur_data)
        login_user(student)
        return redirect('/')
    return render_template(ELJUR_LOGIN, error='Школьник не найден', **args)


@app.route("/eljur_login", methods=['GET', 'POST'])
@cross_origin()
def eljur_login():
    args = {'oauth_eljur_page': ConfigEljur.OAUTH_ELJUR_PAGE}
    if request.method == 'GET':
        return render_template(ELJUR_LOGIN, **args)
    try:
        user_login = request.form['login']
        user_password = request.form['password']
        empty_checker(user_login, user_password)
    except Exception:
        return render_template(ELJUR_LOGIN, error='Некорректные данные', **args)
    eljur_answer = EljurLoginByPassword.login(user_login, user_password)
    return eljur_login_raw(eljur_answer)


@app.route("/eljur_login_oauth")
@cross_origin()
def eljur_login_ouath():
    code = request.args.get('code')
    tg = request.args.get('state')
    tg = None if tg == 'ok' else int(tg)
    eljur_answer = EljurLoginByOauth.login(code)
    return eljur_login_raw(eljur_answer, tg)


@app.route("/logout")
@cross_origin()
def logout():
    logout_user()
    return redirect('/')
