from backend import app
from backend.help import start_debug, init_mail_messages
from backend.queries.help import parse_files


if __name__ == '__main__':
    parse_files()
    start_debug()
    # init_mail_messages()
    app.run(host='0.0.0.0', port=8080)
