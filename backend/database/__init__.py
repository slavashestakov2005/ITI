from . import __db_session
from .__db_session import execute_sql
from .__all_models import *


def get_student_by_params(year: int, name1: str, name2: str, class_n: str, class_l: int):
    students = Student.select_by_name(name1, name2)
    for student in students:
        cls = StudentClass.select(year, student.id)
        if cls is None or cls.class_latter == class_l and cls.class_number == class_n:
            return student
    return None


def decode_result(iti: Iti, code: int):
    if iti.encoding_type == 0:
        return Code.select(iti.id, code)
    elif iti.encoding_type == 1:
        return Barcode.select(iti.id, code)
    return None
