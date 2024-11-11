import os


class Config:
    UPLOAD_FOLDER = 'backend/static'
    TEMPLATES_FOLDER = 'backend/templates'
    DEFAULT_ITI_FOLDER = 'backend/HTML/default_iti'
    HTML_FOLDER = 'backend/HTML'
    DATA_FOLDER = 'backend/data'
    WORDS_FOLDER = 'backend/data/words'
    ALLOWED_EXTENSIONS = {'js', 'css', 'scss', 'map', 'jpg', 'jpeg', 'png', 'gif', 'svg'}
    SECRET_KEY = os.getenv('ALL_SECRET_KEY')
    TEMPLATES_AUTO_RELOAD = True

    HOST = 'http://iti.univers.su/'
    SCANNER_VERSION = os.getenv('SCANNER_VERSION')
    BOT_KEY = os.getenv('TELEGRAM_ITI_API_KEY')
