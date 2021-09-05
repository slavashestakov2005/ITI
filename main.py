from backend import app
from backend.database import create_tables
from backend.help import start_debug, init_mail_messages, FileManager
from backend.queries.help import parse_files
from backend.config import Config


parse_files()
start_debug()
# init_mail_messages()
create_tables()
# FileManager.restore_all()
if not Config.HEROKU:
    app.run(host='0.0.0.0', port=8080)
