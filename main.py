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
    ssl_cert = os.getenv('SSL_CERT_FILE') or 'backend/ssl/iti.local.pem'
    ssl_key = os.getenv('SSL_KEY_FILE') or 'backend/ssl/iti.local-key.pem'
    ssl_context = None
    if os.path.exists(ssl_cert) and os.path.exists(ssl_key):
        ssl_context = (ssl_cert, ssl_key)
    app.run(host='0.0.0.0', port=8000, ssl_context=ssl_context)
