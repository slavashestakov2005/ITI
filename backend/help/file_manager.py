# from ..database import FilesTable, File
import os
import glob
import re

from backend.database import Iti

'''
    correct_slash(str)              Заменяет все слэши на '/'.
    class FileManager               Управляет файлами внутри БД.
        save(file_name)             Добавляет файл в БД.
        save_dir(dir_name)          Добавляет все файлы из dir в БД.
        delete(file_name)           Удаляет файл в БД.
        delete_dir(dir_name)        Удаляет все файлы из dir в БД.
        restore_all()               Создаёт все файлы, записанные в БД.
'''


def correct_slash(s: str):
    return re.sub(r'[/\\]+', '/', s)


# returns paths from ./data/ folder
class FileNames:
    @staticmethod
    def diploma_excel(iti: Iti):
        return '{}/diploma.xlsx'.format(iti.id), 'ИТИ {}. Дипломы.xlsx'.format(iti.id)

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
    def codes_excel(iti: Iti):
        return '{}/codes.xlsx'.format(iti.id), 'ИТИ {}. Кодировка.xlsx'.format(iti.id)

    @staticmethod
    def students_excel(iti: Iti):
        return '{}/students.xlsx'.format(iti.id), 'ИТИ {}. Список школьников'.format(iti.id)


class FileManager:
    @staticmethod
    def save(filename: str) -> None:
        filename = correct_slash(filename)
        with open(filename, 'rb') as f:
            data = f.read()
        # f = File([filename, data])
        # if FilesTable.select(filename).__is_none__:
        #     FilesTable.insert(f)
        # else:
        #     FilesTable.update(f)

    @staticmethod
    def save_dir(directory: str) -> None:
        files = glob.glob(directory + '/**/*.*', recursive=True)
        for file in files:
            FileManager.save(file)

    @staticmethod
    def delete(filename: str) -> None:
        filename = correct_slash(filename)
        # FilesTable.delete(filename)

    @staticmethod
    def delete_dir(directory: str) -> None:
        files = glob.glob(directory + '/**/*.*', recursive=True)
        for file in files:
            FileManager.delete(file)

    @staticmethod
    def restore_all() -> None:
        pass
        # try:
        #     files = FilesTable.select_all()
        # except Exception:
        #     return
        # for file in files:
        #     if not os.path.exists(os.path.dirname(file.name)):
        #         os.makedirs(os.path.dirname(file.name))
        #     with open(file.name, 'wb') as f:
        #         f.write(file.data)
