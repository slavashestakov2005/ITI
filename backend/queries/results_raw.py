import re

from ..database import Barcode, Iti, ItiSubject, ItiSubjectScore, Result, StudentClass, User
from ..help import check_role, UserRoleItiSubject

DEFAULT_MAX_SCORE = 30


def prepare_results(res: str):
    try:
        res = res.replace(',', '.')
        result_sum = sum(map(float, [_ for _ in re.split(r'[^\d\.]+', res) if _]))
        return result_sum
    except Exception:
        return None


def _resolve_max_score(iti_id: int, iti_subject_id: int, student_code: int) -> int | None:
    """
    Возвращает максимальный балл для предмета по классу ученика, если задан.
    """
    barcode = Barcode.select(iti_id, student_code)
    if not barcode:
        return None
    student_class = StudentClass.select(iti_id, barcode.student_id)
    if not student_class:
        return None
    score_cfg = ItiSubjectScore.select(iti_subject_id, student_class.class_number)
    if score_cfg:
        return score_cfg.max_value
    return None


def save_result_(user: User, year: int, subject: int, student_code: int, res: str):
    if student_code == "" or res == "":
        return 1
    ys = ItiSubject.select(year, subject)
    if ys is None:
        return 3
    if not check_role(user=user, roles=[UserRoleItiSubject.ADD_RESULT], iti_id=year, iti_subject_id=ys.id):
        return -1
    result_sum = prepare_results(res)
    if result_sum is None:
        return 5
    max_allowed = _resolve_max_score(year, ys.id, student_code)
    limit = max_allowed if max_allowed is not None else DEFAULT_MAX_SCORE
    if result_sum > limit:
        return 6, limit

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
        if not check_role(user=user, roles=[UserRoleItiSubject.EDIT_RESULT], iti_id=year, iti_subject_id=ys.id):
            return 4
        else:
            Result.update(r)
    else:
        Result.insert(r)
    return 0


def delete_result_(user: User, year: int, year_subject: int, student_code: int):
    if not check_role(user=user, roles=[UserRoleItiSubject.DELETE_RESULT], iti_id=year, iti_subject_id=year_subject):
        return -1
    r = Result.build(year_subject, student_code, 0, 0, 0, 0, allow_empty=True)
    old_r = Result.select_for_student_code(r)
    if old_r is None:
        return 1
    Result.delete_by_student_code(r)
    return 0
