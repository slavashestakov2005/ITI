# from ..database import FilesTable, File
import os
import glob
import re
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
