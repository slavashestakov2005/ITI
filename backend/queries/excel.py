from backend import app
from flask import render_template, request, send_file, redirect
from flask_cors import cross_origin
from flask_login import login_required, current_user
from .help import check_status, check_block_iti, path_to_subject
from .results import page_params
from ..database import Iti
from ..excel import ExcelFullReader, ExcelItiWriter, ExcelResultsReader, ExcelFullWriter, ExcelStudentsReader
from ..config import Config
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
def load_data_from_excel_all():
    file = request.files['file']
    filename = Config.DATA_FOLDER + '/sheet_all.' + file.filename.rsplit('.', 1)[1]
    file.save(filename)
    ExcelFullReader(filename).read()
    return 'OK'


@app.route('/load_data_from_excel_students', methods=['POST'])
@cross_origin()
@login_required
@check_status('admin')
def load_data_from_excel_students():
    try:
        file = request.files['file']
        iti_id = int(request.form['iti_id'])
        filename = Config.DATA_FOLDER + '/students_{}.'.format(iti_id) + file.filename.rsplit('.', 1)[1]
        file.save(filename)
        ExcelStudentsReader(file, iti_id).read()
    except Exception as ex:
        return 'Error: ' + str(ex)
    return 'OK'


@app.route('/download_db', methods=['GET'])
@cross_origin()
@login_required
@check_status('admin')
def download_db():
    ExcelFullWriter(Config.DATA_FOLDER + '/data_all.xlsx').write()
    filename = './data/data_all.xlsx'
    return send_file(filename, as_attachment=True, download_name='ИТИ. Все данные.xlsx')


@app.route('/<int:iti_id>/download_iti', methods=['GET'])
@cross_origin()
@login_required
@check_status('admin')
@check_block_iti()
def download_iti(iti: Iti):
    ExcelItiWriter(Config.DATA_FOLDER + '/data_{}.xlsx'.format(iti.id), iti.id).write()
    filename = './data/data_{}.xlsx'.format(iti.id)
    return send_file(filename, as_attachment=True, download_name='ИТИ {}. Все данные.xlsx'.format(iti.id))


@app.route('/<int:iti_id>/download_diploma', methods=['GET'])
@cross_origin()
@login_required
@check_status('admin')
@check_block_iti()
def download_diploma(iti: Iti):
    filename = './data/diploma_{}.xlsx'.format(iti.id)
    return send_file(filename, as_attachment=True, download_name='ИТИ {}. Дипломы.xlsx'.format(iti.id))


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
