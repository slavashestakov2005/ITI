from backend import app
from flask import render_template, request
from flask_cors import cross_origin
from flask_login import login_required
from .help import check_status, check_block_year, SplitFile
from ..help import init_mail_messages
from ..database import DataBase, SubjectsTable, Subject, YearsTable, Year
from .auto_generator import Generator
from .file_creator import FileCreator
from ..config import Config
'''
    Функции ниже доступны только full, если не указано иного.
    /add_year               add_year()              Создаёт новый год ИТИ.
    /add_subject            add_subject()           Создаёт новый предмет.
    /edit_subject           edit_subject()          Редактирует предмет.
    /delete_subject         delete_subject()        Удаляет предмет.
    /global_settings        global_settings()       Сохраняет глобальные настройки (пароль от почты).
    /db                     db()                    Делает SQL запросы к базе данных.
    /<year>/year_block      year_block()            Блокирует последующее редактирование года для всех.
'''


@app.route("/add_year", methods=['POST'])
@cross_origin()
@login_required
@check_status('full')
@check_block_year()
def add_year():
    name = int(request.form['name'])
    year = YearsTable.select_by_year(name)
    if not year.__is_none__:
        return render_template('subjects_and_years.html', error1='Год уже существует')
    year = Year([name, '', 0])
    YearsTable.insert(year)
    FileCreator.create_year(name)
    Generator.gen_years_lists()
    Generator.gen_years_subjects_list(name)
    return render_template('subjects_and_years.html', error1='Год добавлен')


@app.route("/add_subject", methods=['POST'])
@cross_origin()
@login_required
@check_status('full')
@check_block_year()
def add_subject():
    name = request.form['name']
    subject_type = request.form['type']
    subject = SubjectsTable.select_by_name(name)
    if not subject.__is_none__:
        return render_template('subjects_and_years.html', error2='Предмет уже существует')
    subject = Subject([None, name, subject_type])
    SubjectsTable.insert(subject)
    Generator.gen_subjects_lists()
    return render_template('subjects_and_years.html', error2='Предмет добавлен')


@app.route("/edit_subject", methods=['POST'])
@cross_origin()
@login_required
@check_status('full')
@check_block_year()
def edit_subject():
    id = int(request.form['id'])
    new_name = request.form['new_name']
    subject_type = request.form['new_type']
    subject = SubjectsTable.select_by_id(id)
    if subject.__is_none__:
        return render_template('subjects_and_years.html',  error3='Предмета не существует')
    subject.name = new_name
    subject.type = subject_type
    SubjectsTable.update_by_id(subject)
    Generator.gen_subjects_lists()
    return render_template('subjects_and_years.html', error3='Предмет обнавлён')


@app.route("/delete_subject", methods=['POST'])
@cross_origin()
@login_required
@check_status('full')
@check_block_year()
def delete_subject():
    id = int(request.form['id'])
    subject = SubjectsTable.select_by_id(id)
    if subject.__is_none__:
        return render_template('subjects_and_years.html', error4='Предмета не существует')
    SubjectsTable.delete(subject)
    Generator.gen_subjects_lists()
    return render_template('subjects_and_years.html', error4='Предмет удалён')


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


@app.route('/db')
@cross_origin()
@login_required
@check_status('full')
@check_block_year()
def db():
    sql = request.args.get('sql')
    t = request.args.get('type')
    if t and t != '':
        return str(DataBase.execute(sql))
    DataBase.just_execute(sql)
    return 'OK'


@app.route('/<path:year>/year_block', methods=['POST'])
@cross_origin()
@login_required
@check_status('full')
def year_block(year):
    year = int(year)
    is_block = int(request.form['is_block'])
    year = YearsTable.select_by_year(year)
    if year.__is_none__:
        return render_template(str(year.year) + '/subjects_for_year.html', error8='Этого года нет.', year=year.year)
    year.block = is_block
    YearsTable.update(year)
    data = SplitFile(Config.TEMPLATES_FOLDER + '/' + str(year.year) + '/subjects_for_year.html')
    data.insert_after_comment(' is_block ', '''
                <p><input type="radio" name="is_block" value="0" {0}>Разблокировано</p>
                <p><input type="radio" name="is_block" value="1" {1}>Заблокировано</p>
            '''.format('checked' if is_block == 0 else '', 'checked' if is_block == 1 else ''))
    data.save_file()
    return render_template(str(year.year) + '/subjects_for_year.html', error8='Сохранено.', year=year.year)

