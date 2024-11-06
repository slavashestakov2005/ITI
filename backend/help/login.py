from flask import redirect, render_template, request
from flask_cors import cross_origin
from flask_login import current_user, login_user, logout_user

from backend import app, login
from backend.queries.help import empty_checker, split_class
from ..database import get_student_by_params, Student, StudentEljur, User
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
    if current_user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        try:
            user_login = request.form['login']
            user_password = request.form['password']
            empty_checker(user_login, user_password)
        except Exception:
            return render_template(TEMPLATE, error='Некорректные данные')

        u = User.select_by_login(user_login)
        if u is not None and u.check_password(user_password):
            u.id = -u.id
            login_user(u)
            return redirect('/')
        else:
            return render_template(TEMPLATE, error='Неверные логин или пароль')
    return render_template(TEMPLATE)


def eljur_login_raw(eljur_answer: dict):
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
            login_user(student)
            return redirect('/')
        return render_template(ELJUR_LOGIN, error='Школьник не найден', **args)
    cls_n, cls_l = split_class(eljur_data['class'])
    student = get_student_by_params(8, eljur_data['name1'], eljur_data['name2'], cls_n, cls_l)
    if student is not None:
        StudentEljur.insert(StudentEljur.build(student.id, eljur_data['eljur_id']))
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
    eljur_answer = EljurLoginByOauth.login(code)
    return eljur_login_raw(eljur_answer)


@app.route("/logout")
@cross_origin()
def logout():
    logout_user()
    return redirect('/')
