import os


class Config:
    UPLOAD_FOLDER = 'backend/static'
    TEMPLATES_FOLDER = 'backend/templates'
    EXAMPLES_FOLDER = 'backend/examples'
    EXAMPLES_FOLDER_ = 'backend/_examples'
    HTML_FOLDER = 'backend/HTML'
    DATA_FOLDER = 'backend/data'
    ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'html', 'docx'])
    SECRET_KEY = 'you-will-never-guess'
    TEMPLATES_AUTO_RELOAD = True

    PA = True if os.getenv('PA') else False
    PA_DB_USER = 'iti106'
    PA_DB_PASSWORD = 's1f212fsd5f4sdffs'
    PA_DB_HOST = 'iti106.mysql.pythonanywhere-services.com'
    PA_DB = 'iti106$iti'

    HEROKU = True if os.getenv('HEROKU') else False
    DROP_DB = True if os.getenv('DROP_DB') else False
    DB = os.getenv('DATABASE_URL') if HEROKU else 'backend/database.db'
    DB_COLS_PREFIX = 'c_' if HEROKU else ''
    DB_TABLE_PREFIX = 't_' if HEROKU else ''

    MAIL_SERVER = "smtp.googlemail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = 1
    MAIL_USERNAME = "iti.univers106@gmail.com"
    MAIL_PASSWORD = None
    ADMINS = ['iti.univers106@gmail.com']
