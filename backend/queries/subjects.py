from backend import app
from .help import check_status, check_block_year
from .messages_help import message_timetable_public
from ..database import Message, Year
from flask import render_template
from flask_cors import cross_origin
from flask_login import login_required
'''
    /<year>/public_description     public_description(...)    Публикует описание всех предметов одного года.
'''


def page_args(year: int):
    return {'year': abs(year), 'messages': Message.select_by_year(year)}


@app.route('/<year:year>/public_description')
@cross_origin()
@login_required
@check_status('admin')
@check_block_year()
def public_description(year: int):
    if Year.select(year) is None:
        return render_template(str(year) + '/subjects_for_year.html', error11='Такого года нет.', **page_args(year))
    message_timetable_public(year)
    return render_template(str(year) + '/subjects_for_year.html', error11='Сообщение опубликовано', **page_args(year))
