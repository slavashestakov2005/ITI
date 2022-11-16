import os


class ConfigEljur:
    DEVKEY = os.getenv('ELJUR_DEVKEY')
    QUERY_PART = {'vendor': 'univers', 'out_format': 'json', 'devkey': DEVKEY}

    SERVER_API = 'https://univers.eljur.ru/api/'
    AUTH_URL = SERVER_API + 'auth'
    RULES_URL = SERVER_API + 'getrules'
