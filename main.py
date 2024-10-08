import os
from dotenv import load_dotenv
os.chdir(os.path.dirname(os.path.abspath(__file__)))
load_dotenv('.env')


from backend import app
from backend.help import start_debug, init_mail_messages

import logging

logging.basicConfig(filename="logs.log", level=logging.DEBUG)


start_debug()
init_mail_messages()
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
