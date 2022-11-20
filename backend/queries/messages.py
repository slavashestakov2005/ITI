from backend import app
from .help import check_status, check_block_year, correct_new_line
from ..database import MessagesTable, YearsTable, Message
from flask import render_template, request
from flask_cors import cross_origin
from flask_login import login_required
from .messages_help import send_message_to_telegram
from datetime import datetime


def page_args(year: int):
    return {'year': abs(year), 'messages': MessagesTable.select_by_year(year)}


@app.route('/<year:year>/add_message', methods=['POST'])
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def add_message(year: int):
    try:
        title = correct_new_line(request.form['title'])
        content = correct_new_line(request.form['content'])
        if not request.form['date'] or not request.form['time']:
            point = int(datetime.now().timestamp())
        else:
            date = [int(_) for _ in request.form['date'].split('-')]
            time = [int(_) for _ in request.form['time'].split(':')]
            point = int(datetime(*date, *time).timestamp())
    except Exception:
        return render_template(str(year) + '/subjects_for_year.html', error7='Некорректные данные', **page_args(year))

    if YearsTable.select(year).__is_none__:
        return render_template(str(year) + '/subjects_for_year.html', error7='Этого года нет.', **page_args(year))

    MessagesTable.insert(Message([None, year, title, content, point]))
    send_message_to_telegram(title, content, year)
    return render_template(str(year) + '/subjects_for_year.html', error7='Сохранено.', **page_args(year))


@app.route('/<year:year>/edit_message', methods=['POST'])
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def edit_message(year: int):
    try:
        id_ = int(request.form['id'])
        title = correct_new_line(request.form['title']) if request.form['title'] else None
        content = correct_new_line(request.form['content']) if request.form['content'] else None
        if not request.form['date'] or not request.form['time']:
            point = None
        else:
            date = [int(_) for _ in request.form['date'].split('-')]
            time = [int(_) for _ in request.form['time'].split(':')]
            point = int(datetime(*date, *time).timestamp())
    except Exception:
        return render_template(str(year) + '/subjects_for_year.html', error9='Некорректные данные', **page_args(year))

    message = MessagesTable.select(id_)
    if YearsTable.select(year).__is_none__:
        return render_template(str(year) + '/subjects_for_year.html', error9='Этого года нет.', **page_args(year))
    if message.__is_none__:
        return render_template(str(year) + '/subjects_for_year.html', error9='Такого ID нет.', **page_args(year))
    if title:
        message.title = title
    if content:
        message.content = content
    if point:
        message.time = point
    MessagesTable.update(message)
    return render_template(str(year) + '/subjects_for_year.html', error9='Сохранено.', **page_args(year))


@app.route('/<year:year>/delete_message', methods=['POST'])
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def delete_message(year: int):
    try:
        id_ = int(request.form['id'])
    except Exception:
        return render_template(str(year) + '/subjects_for_year.html', error10='Некорректные данные', **page_args(year))

    message = MessagesTable.select(id_)
    if YearsTable.select(year).__is_none__:
        return render_template(str(year) + '/subjects_for_year.html', error10='Этого года нет.', **page_args(year))
    if message.__is_none__:
        return render_template(str(year) + '/subjects_for_year.html', error10='Такого ID нет.', **page_args(year))
    MessagesTable.delete(message)
    return render_template(str(year) + '/subjects_for_year.html', error10='Сохранено.', **page_args(year))
