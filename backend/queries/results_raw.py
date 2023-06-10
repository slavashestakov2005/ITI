import re
from ..database import Result, StudentCode, User, YearSubject
# from ..help.log import Log
'''
    prepare_results(res: str)       Получает данные из введённой строки результатов
    save_result_(...)               Возвращает код попытки сохранения или обновление результата.
    delete_result_(...)             Возвращает код попытки удаления результата.
'''


def prepare_results(res: str):
    try:
        res = res.replace(',', '.')
        result_sum = sum(map(float, [_ for _ in re.split(r'[^\d\.]+', res) if _]))
        text_result = re.sub('[XxХх]', 'X', ' '.join(re.split(r'[^\dXxХх\.]+', res)))
        return res, result_sum, text_result
    except Exception:
        return None, None, None


def save_result_(user: User, year: int, subject: int, user_id: int, res: str):
    if not user.can_do(subject):
        return -1
    res, result_sum, text_result = prepare_results(res)
    if res is None:
        return 5
    r = Result.build(year, subject, user_id, result_sum, 0, text_result, 0)
    if user_id == "" or res == "":
        return 1
    ys = YearSubject.select(year, subject)
    if ys is None:
        return 3
    if StudentCode.select_by_code(year, user_id, ys.n_d) is None:
        return 2
    old_r = Result.select_for_people(r)
    if old_r is not None:
        if not user.can_do(-1):
            return 4
        else:
            Result.update(r)
            # Log.log('result:update', user, year, subject, user_id, old_r.text_result, text_result)
    else:
        Result.insert(r)
        # Log.log('result:save', user, year, subject, user_id, text_result)
    return 0


def delete_result_(user: User, year: int, subject: int, user_id: int):
    if not user.can_do(-1):
        return -1
    r = Result.build(year, subject, user_id, 0, 0, '', 0, allow_empty=True)
    old_r = Result.select_for_people(r)
    if old_r is None:
        return 1
    Result.delete_by_people(r)
    # Log.log('result:delete', user, year, subject, user_id, old_r.text_result)
    return 0
