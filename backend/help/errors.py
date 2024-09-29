from flask import redirect, render_template, request, url_for
from flask_cors import cross_origin
import logging
from logging.handlers import SMTPHandler
import os

from backend import app
from .config_mail import ConfigMail


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
    return render_template('404' + '.html')


@app.errorhandler(500)
def internal_error(error=None):
    return redirect(url_for('error', status=500))


@app.route("/error")
@cross_origin()
def error():
    status = request.args.get('status')
    return render_template(status + '.html'), status


def init_mail_messages():
    if ConfigMail.MAIL_SERVER:
        auth = None
        if ConfigMail.MAIL_USERNAME or ConfigMail.MAIL_PASSWORD:
            auth = (ConfigMail.MAIL_USERNAME, ConfigMail.MAIL_PASSWORD)
        secure = None
        if ConfigMail.MAIL_USE_TLS:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(ConfigMail.MAIL_SERVER, ConfigMail.MAIL_PORT),
            fromaddr='no-reply@' + ConfigMail.MAIL_SERVER,
            toaddrs=ConfigMail.ADMINS, subject=ConfigMail.TITLE,
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)


class EmptyFieldException(Exception):
    pass
