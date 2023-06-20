import re
from ..database import Result, StudentCode, User, YearSubject
'''
    prepare_results(res: str)       Получает данные из введённой строки результатов
    save_result_(...)               Возвращает код попытки сохранения или обновление результата.
    delete_result_(...)             Возвращает код попытки удаления результата.
'''


def prepare_results(res: str):
    try:
        res = res.replace(',', '.')
        result_sum = sum(map(float, [_ for _ in re.split(r'[^\d\.]+', res) if _]))
        return result_sum
    except Exception:
        return None


def save_result_(user: User, year: int, subject: int, student_code: int, res: str):
    if not user.can_do(subject):
        return -1
    if student_code == "" or res == "":
        return 1
    ys = YearSubject.select(year, subject)
    if ys is None:
        return 3
    sc = StudentCode.select_by_code(year, student_code, ys.n_d)
    if sc is None:
        return 2
    result_sum = prepare_results(res)
    if result_sum is None:
        return 5
    r = Result.build(ys.id, student_code, sc.student, result_sum, 0, 0)
    old_r = Result.select_for_people(r)
    if old_r is not None:
        if not user.can_do(-1):
            return 4
        else:
            Result.update(r)
    else:
        Result.insert(r)
    return 0


def delete_result_(user: User, year: int, subject: int, user_id: int):
    if not user.can_do(-1):
        return -1
    r = Result.build(year, subject, user_id, 0, 0, '', 0, allow_empty=True)
    old_r = Result.select_for_people(r)
    if old_r is None:
        return 1
    Result.delete_by_people(r)
    return 0
