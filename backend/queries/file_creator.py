import json
import os
import shutil

from backend.config import Config
from .auto_generator import Generator
from .help import html_render
from .messages_help import message_save
from ..database import Iti, Subject


class FileCreator:
    @staticmethod
    def __render_default_pages(year: int):
        iti = Iti.select(year)
        Generator.gen_teams(year)
        Generator.gen_ratings(iti)
        Generator.gen_iti_users_list(year)
        Generator.gen_iti_subjects_list(year)
        Generator.gen_timetable(year)
        Generator.gen_iti_block_page(iti)

    @staticmethod
    def __create_default_messages(year: int):
        with open(Config.DATA_FOLDER + '/default_iti_messages.json', 'r', encoding='UTF-8') as f:
            data = json.load(f)
        for line in data:
            message_save(line['title'], line['content'], year, line['priority'])

    @staticmethod
    def create_iti(year: int, send_messages: bool = True):
        directory = Config.TEMPLATES_FOLDER + "/" + str(year)
        if os.path.exists(directory):
            shutil.rmtree(directory)
        data_directory = Config.DATA_FOLDER + "/" + str(year)
        if os.path.exists(data_directory):
            shutil.rmtree(data_directory)
        shutil.copytree(Config.DEFAULT_ITI_FOLDER, directory)
        os.makedirs(data_directory)
        FileCreator.__render_default_pages(year)
        if send_messages:
            FileCreator.__create_default_messages(year)

    @staticmethod
    def create_subjects(iti: Iti, subjects: list):
        subjects = [Subject.select(_) for _ in subjects]
        for subject in subjects:
            template_name = 'iti/subject_ind.html' if subject.type == 'i' else 'iti/subject_group.html'
            args = {} if subject.type == 'i' else {'teams_size': 0}
            file_name = '{}/{}.html'.format(iti.id, subject.id)
            if not os.path.exists(file_name):
                html_render(template_name, file_name, subject_name=subject.name, results={}, scores={}, iti=iti, **args)
