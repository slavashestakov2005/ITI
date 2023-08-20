from backend import app
from flask import render_template, request, send_file, redirect
from flask_cors import cross_origin
from flask_login import login_required
from .help import check_status, check_block_iti
from ..database import Iti
from ..excel import ExcelFullWriter, ExcelFullReader
from ..config import Config


@app.route('/load_data_from_excel_all', methods=['POST'])
@cross_origin()
def load_data_from_excel_all():
    file = request.files['file']
    filename = Config.DATA_FOLDER + '/sheet_all.' + file.filename.rsplit('.', 1)[1]
    file.save(filename)
    ExcelFullReader(filename).read()
    return 'OK'


@app.route('/<int:year>/download_excel', methods=['GET'])
@cross_origin()
@login_required
@check_status('admin')
def download_excel(year: int):
    ExcelFullWriter(year).write(Config.DATA_FOLDER + '/data_{}.xlsx'.format(year))
    filename = './data/data_{}.xlsx'.format(year)
    return send_file(filename, as_attachment=True, download_name='ИТИ {}. Все данные.xlsx'.format(year))


@app.route('/<int:year>/download_diploma', methods=['GET'])
@cross_origin()
@login_required
@check_status('admin')
def download_diploma(year: int):
    filename = './data/diploma_{}.xlsx'.format(year)
    return send_file(filename, as_attachment=True, download_name='ИТИ {}. Дипломы.xlsx'.format(year))


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
