import os
from flask import request, render_template, redirect, url_for
from flask_cors import cross_origin
import logging
from logging.handlers import SMTPHandler
from backend import app


def start_debug():
    os.environ["FLASK_DEBUG"] = "1"


def stop_debug():
    os.environ["FLASK_DEBUG"] = "0"


@app.errorhandler(403)
def forbidden_error(error=None):
    return redirect(url_for('error', status=403))


@app.errorhandler(404)
@app.errorhandler(405)
def not_found_error(error=None):
    return redirect(url_for('error', status=404))


@app.errorhandler(500)
def internal_error(error=None):
    return redirect(url_for('error', status=500))


@app.route("/error")
@cross_origin()
def error():
    status = request.args.get('status')
    return render_template(status + '.html'), status


def init_mail_messages():
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], subject='Ошибка на сайте ИТИ',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

