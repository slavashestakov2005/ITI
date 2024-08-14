from backend import app
from ..database import Iti
from .help import check_access
from .auto_generator import Generator
from flask import render_template
from flask_cors import cross_origin
from flask_login import login_required
'''
    /<iti_id>/create_students_lists         Генерирует списки школьников ИТИ по классам (admin).
'''


@app.route("/<int:iti_id>/create_students_lists")
@cross_origin()
@login_required
@check_access(status='admin', block=True)
def create_students_lists(iti: Iti):
    for class_num in iti.classes_list():
        Generator.gen_students_list(iti.id, int(class_num))
    return render_template('student_edit.html', error4='Таблицы участников обновлены', iti=iti)
