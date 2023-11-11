from backend import app
from flask import render_template, request, send_file
from flask_cors import cross_origin
from flask_login import login_required, current_user
from .auto_generator import Generator
from .file_creator import FileCreator
from .full import _delete_iti
from .help import check_status, check_block_iti, path_to_subject
from .results import page_params
from ..database import Iti, ItiSubject, Subject, Student, Code, School
from ..excel import ExcelFullReader, ExcelItiWriter, ExcelResultsReader, ExcelFullWriter, ExcelStudentsReader,\
    ExcelCodesWriter
from ..config import Config
from ..help import FileNames

'''
    /load_data_from_excel_all               Загружает все данные из Excel (full).
    /load_data_from_excel_students          Загружает список школьников ИТИ (admin).
    /download_db                            Скачивает данные всех ИТИ (admin).
    /<iti_id>/download_iti                  Скачивает данные одного ИТИ (admin).
    /<iti_id>/download_diploma              Скачивает дипломы одного ИТИ (admin).
    /<iti_id>/<path>/load_result            Загружает результаты предмета из Excel (для предметников).
'''


@app.route('/load_data_from_excel_all', methods=['POST'])
@cross_origin()
@login_required
@check_status('full')
def load_data_from_excel_all():
    file = request.files['file']
    filename = Config.DATA_FOLDER + '/sheet_all.' + file.filename.rsplit('.', 1)[1]
    file.save(filename)
    itis_id = ExcelFullReader(filename).read(_delete_iti)
    Generator.gen_iti_lists()
    Generator.gen_subjects_lists()
    subjects = Subject.select_id_dict()
    for iti_id in itis_id:
        iti = Iti.select(iti_id)
        FileCreator.create_iti(iti_id, False)
        Generator.gen_iti_subjects_list(iti_id)
        Generator.gen_teams(iti_id)
        Generator.gen_timetable(iti_id)
        Generator.gen_iti_block_page(iti)
        for class_num in iti.classes_list():
            Generator.gen_students_list(iti.id, int(class_num))
        iti_subjects = ItiSubject.select_by_iti(iti_id)
        FileCreator.create_subjects(iti, [sub.subject_id for sub in iti_subjects])
        for iti_subject in iti_subjects:
            subject = subjects[iti_subject.subject_id]
            filename = '{}/{}.html'.format(iti_id, iti_subject.subject_id)
            if subject.type == 'i':
                Generator.gen_results(iti, iti_subject.subject_id, filename)
            elif subject.type == 'g' or subject.type == 'a':
                Generator.gen_group_results(iti_id, iti_subject.subject_id, filename)
        Generator.gen_ratings(iti)
        students = {_.id: _ for _ in Student.select_by_iti(iti)}
        codes = Code.select_by_iti(iti_id)
        data = []
        schools = School.select_id_dict()
        for code in codes:
            stud = students[code.student_id]
            data.append([stud.name_1, stud.name_2, stud.name_3, stud.school_name(schools), stud.class_name(), code.code])
        store_name, send_name = FileNames.codes_excel(iti)
        ExcelCodesWriter().write(Config.DATA_FOLDER + '/' + store_name, data)
    return 'OK'


@app.route('/load_data_from_excel_students', methods=['POST'])
@cross_origin()
@login_required
@check_status('admin')
def load_data_from_excel_students():
    try:
        file = request.files['file']
        iti_id = int(request.form['iti_id'])
        iti = Iti.select(iti_id)
        store_name, send_name = FileNames.students_excel(iti)
        filename = Config.DATA_FOLDER + '/' + store_name
        file.save(filename)
        answer = ExcelStudentsReader(filename, iti_id).read()
        return answer or 'OK'
    except Exception as ex:
        return 'Error: ' + str(ex)


@app.route('/download_db', methods=['GET'])
@cross_origin()
@login_required
@check_status('admin')
def download_db():
    store_name, send_name = FileNames.data_all_excel()
    ExcelFullWriter(Config.DATA_FOLDER + '/' + store_name).write()
    filename = './data/' + store_name
    return send_file(filename, as_attachment=True, download_name=send_name)


@app.route('/<int:iti_id>/download_iti', methods=['GET'])
@cross_origin()
@login_required
@check_status('admin')
@check_block_iti()
def download_iti(iti: Iti):
    store_name, send_name = FileNames.data_excel(iti)
    ExcelItiWriter(Config.DATA_FOLDER + '/' + store_name, iti.id).write()
    filename = './data/' + store_name
    return send_file(filename, as_attachment=True, download_name=send_name)


@app.route('/<int:iti_id>/download_diploma', methods=['GET'])
@cross_origin()
@login_required
@check_status('admin')
@check_block_iti()
def download_diploma(iti: Iti):
    store_name, send_name = FileNames.diploma_excel(iti)
    filename = './data/' + store_name
    return send_file(filename, as_attachment=True, download_name=send_name)


@app.route('/<int:iti_id>/<path:path3>/load_result', methods=['POST'])
@cross_origin()
@login_required
@check_block_iti()
def load_result(iti: Iti, path3):
    path2 = 'individual'
    url = 'add_result.html'
    try:
        subject = path_to_subject(path3)
        file = request.files['file']
        parts = [x.lower() for x in file.filename.rsplit('.', 1)]
        filename = Config.DATA_FOLDER + '/load_' + str(iti.id) + '_' + str(subject) + '.' + parts[1]
    except Exception:
        params = page_params(iti.id, path2, path3)
        return render_template(url, **params, error6=['[ Некорректные данные ]'])

    file.save(filename)
    # FileManager.save(filename)
    txt = ExcelResultsReader(filename, iti.id, subject).read(current_user)
    params = page_params(iti.id, path2, path3)
    if txt:
        return render_template(url, **params, error6=txt)
    return render_template(url, **params, error6=['[ Сохранено ]'])
