from backend import app
from flask import render_template, request, send_file, redirect
from flask_cors import cross_origin
from flask_login import login_required
import shutil
import glob
import os
from .help import check_status, check_block_year, path_to_subject, is_in_team
from ..help import init_mail_messages, FileManager, AsyncWorker
from ..excel import ExcelFullWriter
from ..database import execute_sql, GroupResult, Message, Result, StudentCode, Subject, SubjectStudent, Team, TeamStudent, Year, YearSubject, YearSubjectScore
from .auto_generator import Generator
from .file_creator import FileCreator
from ..config import Config
'''
    Функции ниже доступны только full, если не указано иного.
    _delete_year()                                          Функция для удаления года ИТИ.
    /add_year                       add_year()              Создаёт новый год ИТИ.
    /delete_year                    delete_year()           Удаляет год ИТИ.
    /add_subject                    add_subject()           Создаёт новый предмет.
    /edit_subject                   edit_subject()          Редактирует предмет.
    /delete_subject                 delete_subject()        Удаляет предмет.
    /global_settings                global_settings()       Сохраняет глобальные настройки (пароль от почты).
    /database                             database()                    Делает SQL запросы к базе данных.
    /<year>/year_block              year_block()            Блокирует последующее редактирование года для всех.
    /load_data_from_excel           load_data_from_excel()  Загружает данные из Excel таблицы.
    /<year>/download_excel          download_excel()        Выгружает данные в Excel.
    /<year>/download_diploma        download_diploma()      Выгружает список грамот в Excel.
    /<year>/download_classes        download_classes()      Выгружает результаты по классам в Excel.
    /<year>/<subject>/download_excel   download_excel2()    Выгружает один предмет в Excel.
'''


def _delete_year(year: int):
    for ys in YearSubject.select_all():
        YearSubjectScore.delete_by_year_subject(ys.id)
        Result.delete_by_year_subject(ys.id)
    StudentCode.delete_by_year(year)
    SubjectStudent.delete_by_year(year)
    Year.delete(year)
    YearSubject.delete_by_year(year)
    Message.delete_by_year(year)

    teams = Team.select_by_year(year)
    for team in teams:
        GroupResult.delete_by_team(team.id)
        TeamStudent.delete_by_team(team.id)
    pl, mn = is_in_team(year)
    TeamStudent.delete_by_team(pl)
    TeamStudent.delete_by_team(mn)
    Team.delete_by_year(year)

    Generator.gen_years_lists()
    dir1, dir2 = Config.UPLOAD_FOLDER + '/' + str(year), Config.TEMPLATES_FOLDER + '/' + str(year)
    simple_dirs = ['/sheet_', '/data_', '/codes_', '/classes_', '/diploma_']
    hard_dirs = ['/data_', '/load_']
    for d in simple_dirs:
        for file in glob.glob(Config.DATA_FOLDER + d + str(year) + '.*'):
            FileManager.delete(file)
            os.remove(file)
    for d in hard_dirs:
        for file in glob.glob(Config.DATA_FOLDER + d + str(year) + '_*.*'):
            FileManager.delete(file)
            os.remove(file)
    FileManager.delete_dir(dir1)
    FileManager.delete_dir(dir2)
    try:
        shutil.rmtree(dir1)
    except FileNotFoundError:
        pass
    try:
        shutil.rmtree(dir2)
    except FileNotFoundError:
        pass


@app.route("/global_settings", methods=['POST'])
@cross_origin()
@login_required
@check_status('full')
@check_block_year()
def global_settings():
    app.config['MAIL_PASSWORD'] = request.form['password']
    init_mail_messages()
    return render_template('settings.html', error2='Успех', email=app.config['MAIL_USERNAME'],
                           admins=str(app.config['ADMINS']), password='Уже введён')


@app.route('/database')
@cross_origin()
@login_required
@check_status('full')
@check_block_year()
def db():
    sql = request.args.get('sql')
    t = request.args.get('type')
    if t and t != '':
        return str(execute_sql(sql))
    execute_sql(sql)
    return 'OK'


def page_args(year: int):
    return {'year': abs(year), 'messages': Message.select_by_year(year)}


@app.route('/<year:year>/year_block')
@cross_origin()
@login_required
@check_status('full')
def year_block(year: int):
    return render_template(str(year) + '/subjects_for_year.html', **page_args(year))


@app.route('/load_data_from_excel', methods=['POST', 'GET'])
@cross_origin()
@login_required
@check_status('full')
@check_block_year()
def load_data_from_excel():
    if request.method == 'GET':
        if AsyncWorker.is_alive():
            return render_template('subjects_and_years.html',  error5='Сохраняется: {}'.format(AsyncWorker.cur_time()))
        return render_template('subjects_and_years.html')
    try:
        year = int(request.form['year']) if request.form['year'] else 0
        file = request.files['file']
        parts = [x.lower() for x in file.filename.rsplit('.', 1)]
        qtype = int(request.form['type'])
        if len(parts) < 2 or (qtype == 1 and (abs(year) <= 2000 or abs(year) >= 2100)):
            raise ValueError
        filename = Config.DATA_FOLDER + '/sheet_' + str(year) + '.' + parts[1]
    except Exception:
        return render_template('subjects_and_years.html',  error5='Некорректные данные')
    if AsyncWorker.is_alive():
        return render_template('subjects_and_years.html',  error5='Один процесс уже запущен')

    if qtype == 1:
        _delete_year(year)
        year_id = Year.insert(Year.build(year, '', 1), return_id=True)
        FileCreator.create_year(year)
        Generator.gen_years_lists()
        Generator.gen_years_subjects_list(year)

    file.save(filename)
    FileManager.save(filename)
    AsyncWorker.call(filename, Year.select(year_id), qtype)

    if qtype == 2:
        os.remove(filename)
        FileManager.delete(filename)
    return render_template('subjects_and_years.html',  error5='Сохранение...')


@app.route('/<year:year>/download_excel', methods=['GET'])
@cross_origin()
@login_required
@check_status('admin')
def download_excel(year: int):
    ExcelFullWriter(year).write(Config.DATA_FOLDER + '/data_{}.xlsx'.format(year))
    filename = './data/data_{}.xlsx'.format(year)
    return send_file(filename, as_attachment=True, download_name='ИТИ {}. Все данные.xlsx'.format(year))


@app.route('/<year:year>/download_diploma', methods=['GET'])
@cross_origin()
@login_required
@check_status('admin')
def download_diploma(year: int):
    filename = './data/diploma_{}.xlsx'.format(year)
    return send_file(filename, as_attachment=True, download_name='ИТИ {}. Дипломы.xlsx'.format(year))
