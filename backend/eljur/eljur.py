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
    def login(login: str, password: str) -> dict:
        s, token = EljurLoginByPassword.auth(login, password)
        if not token:
            return None
        data, headers = make_eljur_query(auth_token=token)
        response = s.get(ConfigEljur.RULES_URL, json=data, headers=headers).json()['response']
        return response


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
    def login(code: str) -> dict:
        s, token = EljurLoginByOauth.auth(code)
        if not token:
            return None
        data, headers = make_eljur_query(auth_token=token)
        response = s.get(ConfigEljur.RULES_URL, json=data, headers=headers).json()['response']
        return response


class EljurHelp:
    @staticmethod
    def parse_data(data: dict) -> dict:
        eljur_id = data['result']['id']
        name1 = data['result']['lastname']
        name2 = data['result']['firstname']
        name3 = data['result']['middlename']
        role = data['result'].get('roles', [])[0]
        cls = None
        for _, student_info in data['result']['relations']['students'].items():
            cls = student_info.get('class')
            break
        return {'eljur_id': eljur_id, 'name1': name1, 'name2': name2, 'name3': name3, 'role': role, 'class': cls}
