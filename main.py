import os
from dotenv import load_dotenv
os.chdir(os.path.dirname(os.path.abspath(__file__)))
load_dotenv('.env')


from backend import app
# from backend.database import create_tables
from backend.help import start_debug
from backend.queries.help import parse_files
from backend.config import Config


parse_files()
start_debug()
# init_mail_messages()
# create_tables()
# FileManager.restore_all() # база данных на сайте обрезает концы файлов
if __name__ == '__main__' and not Config.HEROKU:
    app.run(host='0.0.0.0', port=8080)
