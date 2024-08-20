from requests import Session

from .config_eljur import ConfigEljur


class EljurUser:
    @staticmethod
    def auth(login: str, password: str):
        data = ConfigEljur.QUERY_PART.copy()
        data['login'] = login
        data['password'] = password
        s = Session()
        response = s.post(ConfigEljur.AUTH_URL, json=data).json()['response']
        if response['error']:
            return s, None
        return s, response['result']['token']

    @staticmethod
    def login(login: str, password: str):
        s, token = EljurUser.auth(login, password)
        if not token:
            return None
        data = ConfigEljur.QUERY_PART.copy()
        data['auth_token'] = token
        response = s.get(ConfigEljur.RULES_URL, json=data).json()['response']
        name = response['result']['lastname'] + ' ' + response['result']['firstname']
        return str(response)
