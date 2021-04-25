import os
import shutil
import glob
from backend.config import Config
from .help import SplitFile


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
