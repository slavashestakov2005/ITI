from backend import app
from flask import request, redirect, render_template, url_for
from flask_cors import cross_origin
from flask_login import login_required
from backend.config import Config
from .help import check_status
from ..help.errors import not_found_error
import os


def generate_filename(last_name, new_path, new_name):
    parts = [x.lower() for x in last_name.rsplit('.', 1)]
    if len(parts) < 2 or parts[1] not in Config.ALLOWED_EXTENSIONS:
        return None
    print(os.path.realpath('.'))
    filename = os.path.join(os.path.realpath('.'), Config.UPLOAD_FOLDER, new_path)
    if not os.path.exists(filename):
        os.makedirs(filename)
    return os.path.join(new_path, new_name + '.' + parts[1])


@app.route("/upload", methods=['GET', 'POST'])
@cross_origin()
@login_required
@check_status('admin')
def load():
    if request.method == 'POST':
        file = request.files['file']
        new_path = request.form['new_path']
        new_name = request.form['new_name']
        filename = generate_filename(file.filename, new_path, new_name)
        if filename:
            file.save(os.path.join(Config.UPLOAD_FOLDER, filename))
            return redirect(filename)
    return render_template('upload.html')


@app.route('/<path:path>/edit')
@cross_origin()
@login_required
@check_status('full')
def edit(path):
    print("Here : " + path)
    return redirect(url_for('editor', file_text=path))


@app.route('/editor')
@cross_origin()
@login_required
@check_status('full')
def editor():
    file_name = request.args.get('file_text')
    try:
        with open(Config.TEMPLATES_FOLDER + '/' + file_name, 'r', encoding='UTF-8') as f:
            file_text = f.read()
    except FileNotFoundError as e:
        return not_found_error()
    return render_template('file_edit.html', file_text=file_text, file_name=file_name)


@app.route('/save_file',  methods=['POST'])
@cross_origin()
@login_required
@check_status('full')
def save_file():
    file_name = request.form['file_name']
    file_text = request.form['file_text']
    print(file_name + ":\n" + file_text)
    with open(Config.TEMPLATES_FOLDER + '/' + file_name, 'w', encoding='UTF-8') as f:
        f.write(file_text)
    return render_template('file_edit.html', file_text=file_text, file_name=file_name, error="Файл сохранён")

