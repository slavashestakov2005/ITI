from backend import app
from ..database import Student, StudentClass, Iti
from .help import check_status, check_block_iti
from .auto_generator import Generator
from flask import render_template, send_file, request, jsonify
from flask_cors import cross_origin
from flask_login import login_required
'''
    /<iti_id>/student_info              Возвращает информацию по ID школьника (admin).
    /<iti_id>/create_students_lists     Генерирует списки школьников ИТИ по классам.
'''


@app.route("/<int:iti_id>/student_info", methods=['POST'])
@cross_origin()
@login_required
@check_status('admin')
@check_block_iti()
def student_info(iti: Iti):
    student_id = request.form['student_id']
    student = Student.select(student_id)
    if not student:
        return jsonify({'status': 'Error'})
    student_class = StudentClass.select(iti.id, student_id)
    if not student_class:
        return jsonify({'status': 'Error'})
    return jsonify({'status': 'OK', 'student': student.json(), 'student_class': student_class.json()})


@app.route("/<int:iti_id>/create_students_lists")
@cross_origin()
@login_required
@check_status('admin')
@check_block_iti()
def create_students_lists(iti: Iti):
    for class_num in iti.classes:
        Generator.gen_students_list(iti.id, int(class_num))
    return render_template('student_edit.html', error4='Таблицы участников обновлены', iti=iti)
