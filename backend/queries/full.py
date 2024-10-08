from flask import render_template, request
from flask_cors import cross_origin
from flask_login import login_required
import glob
import os
import shutil

from backend import app
from .auto_generator import Generator
from .help import check_access
from ..config import Config
from ..database import Barcode, Code, execute_sql, GroupResult, Iti, ItiSubject, ItiSubjectScore, Message, Result,\
      SubjectStudent, Team, TeamConsent, TeamStudent
from ..help import ConfigMail, init_mail_messages, UserRoleGlobal, UserRoleIti

'''
    /global_settings                        Сохраняет глобальные настройки (пароль от почты) (full).
    /db                                     Делает SQL запросы к базе данных (full).
    /<iti_id>/year_block                    Блокирует последующее редактирование года для всех (admin).
    /restart                                Перезагружает сайт (full).
'''


def _delete_iti(year: int):
    for ys in ItiSubject.select_all():
        ItiSubjectScore.delete_by_iti_subject(ys.id)
        Result.delete_by_iti_subject(ys.id)
        SubjectStudent.delete_by_iti_subject(ys.id)
    Barcode.delete_by_iti(year)
    Code.delete_by_iti(year)
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
    dir3 = Config.DATA_FOLDER + '/' + str(year)
    simple_dirs = ['/sheet_', '/data_', '/codes_', '/classes_', '/diploma_', '/barcodes_']
    hard_dirs = ['/data_', '/load_']
    for d in simple_dirs:
        for file in glob.glob(Config.DATA_FOLDER + d + str(year) + '.*'):
            os.remove(file)
    for d in hard_dirs:
        for file in glob.glob(Config.DATA_FOLDER + d + str(year) + '_*.*'):
            os.remove(file)
    for file in glob.glob(Config.DATA_FOLDER + '/{}/'.format(year) + "*.*"):
        os.remove(file)
    dirs = [dir1, dir2, dir3]
    for cur_dir in dirs:
        try:
            shutil.rmtree(cur_dir)
        except FileNotFoundError:
            pass


@app.route("/global_settings", methods=['POST'])
@cross_origin()
@login_required
@check_access(roles=[UserRoleGlobal.FULL])
def global_settings():
    app.config['MAIL_PASSWORD'] = request.form['password']
    init_mail_messages()
    return render_template('settings.html', error2='Успех', email=ConfigMail.MAIL_USERNAME,
                           admins=str(ConfigMail.ADMINS), password='Уже введён')


@app.route('/db')
@cross_origin()
@login_required
@check_access(roles=[UserRoleGlobal.FULL])
def db():
    sql = request.args.get('sql')
    t = request.args.get('type')
    if t and t != '':
        return str(execute_sql(sql, True))
    execute_sql(sql, False)
    return 'OK'


@app.route('/<int:iti_id>/year_block')
@cross_origin()
@login_required
@check_access(roles=[UserRoleIti.ADMIN])
def year_block(iti: Iti):
    return render_template(str(iti.id) + '/year_block.html', iti=iti)


@app.route('/restart')
@cross_origin()
@login_required
@check_access(roles=[UserRoleGlobal.FULL])
def restart():
    with open('.restart-app', 'w') as f:
        pass
    return 'Файл перезагрузки создан, ожидайте'


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


@app.get('/shutdown')
@cross_origin()
@login_required
@check_access(roles=[UserRoleGlobal.FULL])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'
