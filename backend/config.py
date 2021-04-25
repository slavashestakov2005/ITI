class Config:
    UPLOAD_FOLDER = 'backend/static'
    TEMPLATES_FOLDER = 'backend/templates'
    EXAMPLES_FOLDER = 'backend/examples'
    HTML_FOLDER = 'backend/HTML'
    ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'html'])
    SECRET_KEY = 'you-will-never-guess'

    '''
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['your-email@example.com']'''

    MAIL_SERVER = "smtp.googlemail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = 1
    MAIL_USERNAME = "qrup211@gmail.com"
    MAIL_PASSWORD = "tima4102!"
    ADMINS = ['v.shestakov@student.univers.su']


