import os
import shutil
import glob
from backend.config import Config
from .help import SplitFile
from ..database import SubjectsTable
'''
    class FileCreator           Создаёт необходимые файлы.
        create_year(year)                   Создаёт стандартные страницы ИТИ (копирует шаблоны).
        create_subjects(year, subject)      Создаёт html-страницу для нужного года и предмета.
'''


class FileCreator:
    @staticmethod
    def create_year(year: int):
        directory = Config.TEMPLATES_FOLDER + "/" + str(year)
        if os.path.exists(directory):
            shutil.rmtree(directory)
        shutil.copytree(Config.EXAMPLES_FOLDER, directory)
        files = glob.glob(directory + '/**/*.html', recursive=True)
        text = 'ИТИ-' + str(year)
        for file_name in files:
            data = SplitFile(file_name)
            data.insert_after_comment(' year ', text)
            data.save_file()

    @staticmethod
    def create_subjects(year: int, subjects: list):
        subjects = [SubjectsTable.select_by_id(_) for _ in subjects]
        directory = Config.TEMPLATES_FOLDER + "/" + str(year) + "/"
        s = set()
        data = SplitFile(Config.HTML_FOLDER + "/1.html")
        data.insert_after_comment(' year ', 'ИТИ-' + str(year))
        for subject in subjects:
            file_name = directory
            if subject.type == 'i':
                file_name += 'individual/'
                tour_name = 'Индивидуальный тур'
            elif subject.type == 'g':
                file_name += 'group/'
                tour_name = 'Групповой тур'
            else:
                file_name += 'team/'
                tour_name = 'Командный тур'
            file_name += str(subject.id) + ".html"
            if not os.path.exists(file_name):
                data.insert_after_comment(' tour_name ', tour_name)
                data.insert_after_comment(' subject_name ', subject.name)
                data.save_file(file_name)
                s.add(file_name)
        for file_name in glob.glob(directory + '**/*.html', recursive=False):
            file_name = file_name.replace('\\', '/')
            if file_name not in s:
                os.remove(file_name)
