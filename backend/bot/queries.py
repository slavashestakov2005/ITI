import requests

from .config import Config


def get_student(tg_id: int) -> list[tuple[str, int, float, float]]:
    args = {'tg_id': tg_id, 'api_key': Config.BOT_KEY}
    r = requests.post(Config.URL_GET_STUDENT, json=args).json()
    if r['status'] != 'OK':
        return None
    return r['data']


def get_results_for_student(student_id: int, iti_id: int) -> list[tuple[str, int, float, float]]:
    args = {'student_id': student_id, 'iti_id': iti_id, 'api_key': Config.BOT_KEY}
    r = requests.post(Config.URL_GET_RESULTS, json=args).json()
    if r['status'] != 'OK':
        return None
    return r['results']
