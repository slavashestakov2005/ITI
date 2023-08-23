from backend import app
from .help import check_status, check_block_iti
from .messages_help import message_timetable_public
from ..database import Iti
from flask import render_template
from flask_cors import cross_origin
from flask_login import login_required
'''
    /<iti_id>/public_description            Публикует описание всех предметов одного года (admin).
'''


@app.route('/<int:iti_id>/public_description')
@cross_origin()
@login_required
@check_status('admin')
@check_block_iti()
def public_description(iti: Iti):
    message_timetable_public(iti.id)
    return render_template(str(iti.id) + '/subjects_for_year.html', error11='Сообщение опубликовано')
