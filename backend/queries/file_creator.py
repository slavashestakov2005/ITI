import os
import shutil
from backend.config import Config
from .help import html_render
from .messages_help import message_save
from ..database import Subject, Iti
from ..help import FileManager
import json


class FileCreator:
    @staticmethod
    def __render_default_pages__(year: int):
        html_render('iti/rating_students.html', str(year) + '/rating_students.html', results={}, students={}, subjects={},
                    classes=[], student_group_results={}, subjects_days={}, ind_res_per_day=0, year=year)
        html_render('iti/rating_students_check.html', str(year) + '/rating_students_check.html', results={}, students={},
                    subjects={}, classes=[], check_marks={}, student_group_results={}, subjects_days={}, ind_res_per_day=0)
        html_render('iti/rating_classes.html', str(year) + '/rating_classes.html', classes=[], results=[])
        html_render('iti/rating_teams.html', str(year) + '/rating_teams.html', team_results={}, ind_subjects={},
                    team_subjects={}, team_student={}, teams={}, students={}, student_results={}, subjects_days={}, ind_res_per_day=0)
        html_render('iti/rating.html', str(year) + '/rating.html', results={}, students={})

    @staticmethod
    def __create_default_messages__(year: int):
        with open(Config.DATA_FOLDER + '/default_iti_messages.json', 'r', encoding='UTF-8') as f:
            data = json.load(f)
        for line in data:
            message_save(line['title'], line['content'], year, line['priority'])

    @staticmethod
    def create_iti(year: int, send_messages: bool = True):
        directory = Config.TEMPLATES_FOLDER + "/" + str(year)
        if os.path.exists(directory):
            shutil.rmtree(directory)
            FileManager.delete_dir(directory)
        data_directory = Config.DATA_FOLDER + "/" + str(year)
        if os.path.exists(data_directory):
            shutil.rmtree(data_directory)
            FileManager.delete_dir(data_directory)
        shutil.copytree(Config.DEFAULT_ITI_FOLDER, directory)
        os.makedirs(data_directory)
        FileManager.save_dir(directory)
        FileCreator.__render_default_pages__(year)
        if send_messages:
            FileCreator.__create_default_messages__(year)

    @staticmethod
    def create_subjects(iti: Iti, subjects: list):
        subjects = [Subject.select(_) for _ in subjects]
        for subject in subjects:
            template_name = 'iti/subject_ind.html' if subject.type == 'i' else 'iti/subject_group.html'
            file_name = '{}/{}.html'.format(iti.id, subject.id)
            if not os.path.exists(file_name):
                html_render(template_name, file_name, subject_name=subject.name, results={}, scores={}, iti=iti)
