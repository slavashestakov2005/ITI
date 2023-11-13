import re
from ..database import Result, User, ItiSubject, Iti


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
    ys = ItiSubject.select(year, subject)
    if ys is None:
        return 3
    result_sum = prepare_results(res)
    if result_sum is None:
        return 5
    if result_sum > 30:
        return 6

    iti = Iti.select(year)
    if iti is None:
        return 7
    if iti.encoding_type == 1:
        result = Result.select_by_code(student_code)
        if result and result.iti_subject_id != ys.id:
            return 8

    r = Result.build(ys.id, student_code, 0, result_sum, 0, 0)
    old_r = Result.select_for_student_code(r)
    if old_r is not None:
        if not user.can_do(-1):
            return 4
        else:
            Result.update(r)
    else:
        Result.insert(r)
    return 0


def delete_result_(user: User, year_subject: int, student_code: int):
    if not user.can_do(-1):
        return -1
    r = Result.build(year_subject, student_code, 0, 0, 0, 0, allow_empty=True)
    old_r = Result.select_for_student_code(r)
    if old_r is None:
        return 1
    Result.delete_by_student_code(r)
    return 0
