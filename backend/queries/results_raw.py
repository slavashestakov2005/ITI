import re
from ..database import User, Result, StudentsCodesTable, YearsSubjectsTable, ResultsTable
from ..help import Log
'''
    prepare_results(res: str)       Получает данные из введённой строки результатов
    save_result_(...)               Возвращает код попытки сохранения или обновление результата.
    delete_result_(...)             Возвращает код попытки удаления результата.
'''


def prepare_results(res: str):
    try:
        res = res.replace(',', '.')
        result_sum = sum(map(float, re.split(r'[^\d\.]+', res)))
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
    r = Result([year, subject, user_id, result_sum, 0, text_result, 0])
    if user_id == "" or res == "":
        return 1
    if StudentsCodesTable.select_by_code(year, user_id).__is_none__:
        return 2
    if YearsSubjectsTable.select(year, subject).__is_none__:
        return 3
    old_r = ResultsTable.select_for_people(r)
    if not old_r.__is_none__:
        if not user.can_do(-1):
            return 4
        else:
            ResultsTable.update(r)
            Log.log('result:update', user, year, subject, user_id, old_r.text_result, text_result)
    else:
        ResultsTable.insert(r)
        Log.log('result:save', user, year, subject, user_id, text_result)
    return 0


def delete_result_(user: User, year: int, subject: int, user_id: int):
    if not user.can_do(-1):
        return -1
    r = Result([year, subject, user_id, 0, 0, '', 0])
    old_r = ResultsTable.select_for_people(r)
    if old_r.__is_none__:
        return 1
    ResultsTable.delete_by_people(r)
    Log.log('result:delete', user, year, subject, user_id, old_r.text_result)
    return 0
