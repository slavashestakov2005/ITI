from backend import app
from flask import render_template, request, send_file, redirect
from flask_cors import cross_origin
from flask_login import login_required
import shutil
import glob
import os
from .help import check_status
from ..help import init_mail_messages, FileManager, ConfigMail
from ..database import execute_sql, GroupResult, Message, Result, Barcode, SubjectStudent, Team, TeamStudent, Iti,\
    ItiSubject, ItiSubjectScore, TeamConsent
from .auto_generator import Generator
from ..config import Config
'''
    Функции ниже доступны только full, если не указано иного.
    _delete_iti()                                           Функция для удаления ИТИ.
    /add_year                       add_year()              Создаёт новый год ИТИ.
    /delete_year                    delete_year()           Удаляет год ИТИ.
    /add_subject                    add_subject()           Создаёт новый предмет.
    /edit_subject                   edit_subject()          Редактирует предмет.
    /delete_subject                 delete_subject()        Удаляет предмет.
    /global_settings                global_settings()       Сохраняет глобальные настройки (пароль от почты).
    /database                             database()                    Делает SQL запросы к базе данных.
    /<year>/year_block              year_block()            Блокирует последующее редактирование года для всех.
'''


def _delete_iti(year: int):
    for ys in ItiSubject.select_all():
        ItiSubjectScore.delete_by_iti_subject(ys.id)
        Result.delete_by_iti_subject(ys.id)
        SubjectStudent.delete_by_iti_subject(ys.id)
    Barcode.delete_by_iti(year)
    Iti.delete(year)
    ItiSubject.delete_by_iti(year)
    Message.delete_by_iti(year)

    teams = Team.select_by_iti(year)
    for team in teams:
        GroupResult.delete_by_team(team.id)
        TeamStudent.delete_by_team(team.id)
    TeamConsent.delete_by_iti(year)
    Team.delete_by_iti(year)

    Generator.gen_iti_lists()
    dir1, dir2 = Config.UPLOAD_FOLDER + '/' + str(year), Config.TEMPLATES_FOLDER + '/' + str(year)
    simple_dirs = ['/sheet_', '/data_', '/codes_', '/classes_', '/diploma_', '/barcodes_']
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
def global_settings():
    app.config['MAIL_PASSWORD'] = request.form['password']
    init_mail_messages()
    return render_template('settings.html', error2='Успех', email=ConfigMail.MAIL_USERNAME,
                           admins=str(ConfigMail.ADMINS), password='Уже введён')


@app.route('/db')
@cross_origin()
@login_required
@check_status('full')
def db():
    sql = request.args.get('sql')
    t = request.args.get('type')
    if t and t != '':
        return str(execute_sql(sql))
    execute_sql(sql)
    return 'OK'


@app.route('/<int:iti_id>/year_block')
@cross_origin()
@login_required
@check_status('full')
def year_block(iti_id: int):
    return render_template(str(iti_id) + '/year_block.html')
