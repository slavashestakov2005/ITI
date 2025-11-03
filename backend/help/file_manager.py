from datetime import datetime, timezone
import glob
import re

from backend.database import Iti

'''
    get_timestamp(*args)            Возвращает int - временную точку вычисленную от аргументов (UTC now, если нет аргументов).
    krsk_time(utc_time)             Возвращает время в Красноярске для заднного времени в UTC/
    correct_slash(str)              Заменяет все слэши на '/'.
'''


def get_timestamp(*args):
    if not len(args):
        point = datetime.now(timezone.utc)
    else:
        point = datetime(*args, tzinfo=timezone.utc)
    return int(point.timestamp())


def krsk_time(point: int):
    return datetime.utcfromtimestamp(point + 25200)


def correct_slash(s: str):
    return re.sub(r'[/\\]+', '/', s)


# returns paths from ./data/ folder
class FileNames:
    @staticmethod
    def diploma_excel(iti: Iti):
        return '{}/diploma.xlsx'.format(iti.id), 'ИТИ {}. Дипломы.xlsx'.format(iti.id)

    @staticmethod
    def diploma_excel_teamed(iti: Iti):
        return '{}/diploma_teamed.xlsx'.format(iti.id), 'ИТИ {}. Дипломы командных школьников.xlsx'.format(iti.id)

    @staticmethod
    def data_excel(iti: Iti):
        return '{}/data.xlsx'.format(iti.id), 'ИТИ {}. Все данные.xlsx'.format(iti.id)

    @staticmethod
    def data_all_excel():
        return 'data_all.xlsx', 'ИТИ. Все данные.xlsx'

    @staticmethod
    def barcodes_word(iti: Iti):
        return '{}/barcodes.docx'.format(iti.id), 'ИТИ {}. Бланки для кодировки.docx'.format(iti.id)
    
    @staticmethod
    def barcodes_for_teamed_word(iti: Iti):
        return '{}/barcodes_teamed.docx'.format(iti.id), 'ИТИ {}. Бланки для кодировки командных школьников.docx'.format(iti.id)

    @staticmethod
    def codes_excel(iti: Iti):
        return '{}/codes.xlsx'.format(iti.id), 'ИТИ {}. Кодировка.xlsx'.format(iti.id)

    @staticmethod
    def students_excel(iti: Iti):
        return '{}/students.xlsx'.format(iti.id), 'ИТИ {}. Список школьников.xlsx'.format(iti.id)

    @staticmethod
    def barcodes_excel(iti: Iti, start_code: int, end_code: int):
        args = iti.id, start_code, end_code
        return '{}/barcodes_{}_{}.xlsx'.format(*args), 'ИТИ {}. Штрих-коды {}-{}.xlsx'.format(*args)
