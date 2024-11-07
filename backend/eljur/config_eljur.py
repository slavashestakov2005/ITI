import os
from ..config import Config


class ConfigEljur:
    DEVID = os.getenv('ELJUR_DEVID')
    DEVKEY = os.getenv('ELJUR_DEVKEY')
    QUERY_PART = {'vendor': 'univers', 'out_format': 'json', 'devkey': DEVKEY}
    HEADERS = {"User-Agent": Config.HOST}

    SERVER_API = 'https://univers.eljur.ru/api/'
    AUTH_URL = SERVER_API + 'auth'
    RULES_URL = SERVER_API + 'getrules'

    OAUTH_ITI_PAGE = Config.HOST + 'eljur_login_oauth'
    OAUTH_ELJUR_PAGE = f'https://auth.eljur.ru/auth/{DEVID}?client_id={DEVID}&response_type=code&redirect_uri={OAUTH_ITI_PAGE}&state=ok'
    OAUTH_URL = f'https://auth.eljur.ru/oauthtoken?devkey={DEVKEY}&grant_type=authorization_code&client_id={DEVID}&redirect_uri={OAUTH_ITI_PAGE}&code='

    OAUTH_ELJUR_PAGE_TG = f'https://auth.eljur.ru/auth/{DEVID}?client_id={DEVID}&response_type=code&redirect_uri={OAUTH_ITI_PAGE}&state={{}}'
