from requests import Session

from .config_eljur import ConfigEljur


def make_eljur_query(**kwargs) -> tuple[dict, dict]:
    data = ConfigEljur.QUERY_PART.copy()
    headers = ConfigEljur.HEADERS.copy()
    for key, val in kwargs.items():
        data[key] = val
    return data, headers


class EljurLoginByPassword:
    @staticmethod
    def auth(login: str, password: str) -> tuple[Session, str]:
        data, headers = make_eljur_query(login=login, password=password)
        s = Session()
        response = s.post(ConfigEljur.AUTH_URL, json=data, headers=headers).json()['response']
        if response['error']:
            return s, None
        return s, response['result']['token']

    @staticmethod
    def login(login: str, password: str):
        s, token = EljurLoginByPassword.auth(login, password)
        if not token:
            return None
        data, headers = make_eljur_query(auth_token=token)
        response = s.get(ConfigEljur.RULES_URL, json=data, headers=headers).json()['response']
        name = response['result']['lastname'] + ' ' + response['result']['firstname']
        return str(response)


class EljurLoginByOauth:
    @staticmethod
    def auth(code: str) -> tuple[Session, str]:
        data, headers = make_eljur_query()
        s = Session()
        response = s.get(ConfigEljur.OAUTH_URL + code, json=data, headers=headers).json()
        if 'error' in response:
            return s, None
        return s, response['access_token']

    @staticmethod
    def login(code: str):
        s, token = EljurLoginByOauth.auth(code)
        if not token:
            return None
        data, headers = make_eljur_query(auth_token=token)
        response = s.get(ConfigEljur.RULES_URL, json=data, headers=headers).json()['response']
        name = response['result']['lastname'] + ' ' + response['result']['firstname']
        return str(response)
