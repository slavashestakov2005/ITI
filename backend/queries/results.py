from backend import app
from backend.help.errors import forbidden_error
from ..database import ResultsTable, Result
from flask import render_template, request
from flask_cors import cross_origin
from flask_login import login_required, current_user
'''
    /<path1>/<path2>/<path3>/add_result     add_result(...)     redirect на страницу редактирования (для предметников).
    /<path1>/<path2>/<path3>/save_result    save_result(...)    Сохранение результатов (для предметников).
'''


@app.route('/<path:path1>/<path:path2>/<path:path3>/add_result')
@cross_origin()
@login_required
def add_result(path1, path2, path3):
    subject = int(path3[:-5])
    if not current_user.can_do(subject):
        return forbidden_error()
    print('Add result ', path1, path2, path3)
    return render_template('add_result.html', year=path1, subject=subject)


@app.route('/<path:path1>/<path:path2>/<path:path3>/save_result', methods=['POST'])
@cross_origin()
@login_required
def save_result(path1, path2, path3):
    year = int(path1)
    subject = int(path3[:-5])
    user_id = request.form['code']
    result = request.form['result']
    if not current_user.can_do(subject):
        return forbidden_error()
    ResultsTable.insert(Result([year, subject, user_id, result]))
    return render_template('add_result.html', year=year, subject=subject,
                           error='Результат участника ' + str(user_id) + ' сохранён')
