import os


class ConfigMail:
    MAIL_SERVER = "smtp.googlemail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = 1
    MAIL_USERNAME = "iti.univers106@gmail.com"
    MAIL_PASSWORD = os.getenv('HELP_MAIL_PASS')
    ADMINS = ['iti.univers106@gmail.com']
    TITLE = 'Ошибка на сайте ИТИ'
