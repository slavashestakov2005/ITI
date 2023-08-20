import os
import shutil
import glob
from backend.config import Config
from .help import SplitFile, html_render
from ..database import Subject, Iti
from ..help import FileManager
'''
    class FileCreator           Создаёт необходимые файлы.
        create_iti(year)                    Создаёт стандартные страницы ИТИ (копирует шаблоны).
        create_subjects(year, subject)      Создаёт html-страницу для нужного года и предмета.
'''


class FileCreator:
    @staticmethod
    def __render_defaul_pages__(year: int):
        html_render('rating_students.html', str(year) + '/rating_students.html', results={}, students={}, subjects={},
                    classes=[])
        html_render('rating_students_check.html', str(year) + '/rating_students_check.html', results={}, students={},
                    subjects={}, classes=[], check_marks={})
        html_render('rating_classes.html', str(year) + '/rating_classes.html', classes=[], results=[])
        html_render('rating_teams.html', str(year) + '/rating_teams.html', team_results={}, ind_subjects={},
                    team_subjects={}, team_student={}, teams={}, students={}, student_results={})
        html_render('rating.html', str(year) + '/rating.html', results={}, students={})

    @staticmethod
    def create_iti(year: int):
        directory = Config.TEMPLATES_FOLDER + "/" + str(year)
        if os.path.exists(directory):
            shutil.rmtree(directory)
            FileManager.delete_dir(directory)
        shutil.copytree(Config.EXAMPLES_FOLDER, directory)
        FileManager.save_dir(directory)
        files = glob.glob(directory + '/**/*.html', recursive=True)
        text = 'ИТИ-' + str(abs(year))
        for file_name in files:
            data = SplitFile(file_name)
            data.replace_comment(' {year} ', text)
            data.save_file()
        FileCreator.__render_defaul_pages__(year)

    @staticmethod
    def create_subjects(iti: Iti, subjects: list):
        subjects = [Subject.select(_) for _ in subjects]
        for subject in subjects:
            template_name = 'subject_ind.html' if subject.type == 'i' else 'subject_group.html'
            file_name = '{}/{}.html'.format(iti.id, subject.id)
            if not os.path.exists(file_name):
                html_render(template_name, file_name, subject_name=subject.name, results={}, scores={}, iti=iti)
