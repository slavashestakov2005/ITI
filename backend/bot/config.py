import os


class Config:
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    TELEGRAM_BOT_ID = int(TELEGRAM_TOKEN.split(':')[0])
    TELEGRAM_ADMIN_CHAT_FEEDBACK = [int(part) for part in os.getenv('TELEGRAM_CHAT_FEEDBACK').split('_')]
    TELEGRAM_ADMIN_CHAT_PROBLEM = [int(part) for part in os.getenv('TELEGRAM_CHAT_PROBLEM').split('_')]

    DB = 'backend/database.db'

    HOST = 'http://iti.univers.su/'
    BOT_KEY = os.getenv('TELEGRAM_ITI_API_KEY')
    URL_QUERIES = HOST + 'api/bot/'
    URL_GET_STUDENT = URL_QUERIES + 'get_student'
    URL_GET_RESULTS = URL_QUERIES + 'get_results'
