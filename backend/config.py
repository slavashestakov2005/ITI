import os


class Config:
    UPLOAD_FOLDER = 'backend/static'
    TEMPLATES_FOLDER = 'backend/templates'
    DEFAULT_ITI_FOLDER = 'backend/HTML/default_iti'
    HTML_FOLDER = 'backend/HTML'
    DATA_FOLDER = 'backend/data'
    WORDS_FOLDER = 'backend/data/words'
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'html', 'docx'}
    SECRET_KEY = os.getenv('ALL_SECRET_KEY')
    TEMPLATES_AUTO_RELOAD = True

    HOST = 'http://iti.univers.su/'
