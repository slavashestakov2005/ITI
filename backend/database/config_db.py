import os
from ..config import Config


class ConfigDB:
    PA = True if os.getenv('PA') else False
    PA_DB_USER = 'iti106'
    PA_DB_PASSWORD = '**********'
    PA_DB_HOST = 'iti106.mysql.pythonanywhere-services.com'
    PA_DB = 'iti106$iti'

    DROP_DB = True if os.getenv('DROP_DB') else False
    DB = os.getenv('DATABASE_URL') if Config.HEROKU else 'backend/database.db'
    DB_COLS_PREFIX = 'c_' if Config.HEROKU else ''
    DB_TABLE_PREFIX = 't_' if Config.HEROKU else ''
