from .help import SplitFile, all_templates
from ..database import YearsTable, SubjectsTable, YearsSubjectsTable
from backend.config import Config
import glob


class Generate:
    @staticmethod
    def gen_years_lists():
        years = YearsTable.select_all()
        type1 = type2 = type3 = '\n'
        for year in years:
            type1 += '<a href="' + str(year.year) + '/main.html">ИТИ-' + str(year.year) + "</a>\n"
            type2 += '<a href="../' + str(year.year) + '/main.html">ИТИ-' + str(year.year) + "</a>\n"
            type3 += '<a href="../../' + str(year.year) + '/main.html">ИТИ-' + str(year.year) + "</a>\n"
        for file_name in all_templates():
            data = SplitFile(file_name)
            data.insert_after_comment(' list of years (1) ', type1)
            data.insert_after_comment(' list of years (2) ', type2)
            data.insert_after_comment(' list of years (3) ', type3)
            data.save_file()

    @staticmethod
    def gen_subjects_lists():
        subjects = SubjectsTable.select_all()
        type1 = type2 = type3 = type4 = type5 = type6 = '\n'
        for subject in subjects:
            text1 = '<p><input type="checkbox" name="status" value="' + str(subject.id) + '">' + subject.name + '</p>\n'
            text2 = '<p>[ ' + str(subject.id) + ' ] ' + subject.name + "</p>\n"
            if subject.type == 'i':
                type1 += text1
                type4 += text2
            elif subject.type == 'g':
                type2 += text1
                type5 += text2
            else:
                type3 += text1
                type6 += text2
        for file_name in all_templates():
            data = SplitFile(file_name)
            data.insert_after_comment(' list of individual tours (1) ', type1)
            data.insert_after_comment(' list of group tours (1) ', type2)
            data.insert_after_comment(' list of another tours (1) ', type3)
            data.insert_after_comment(' list of individual tours (2) ', type4)
            data.insert_after_comment(' list of group tours (2) ', type5)
            data.insert_after_comment(' list of another tours (2) ', type6)
            data.save_file()

    @staticmethod
    def gen_years_subjects_list(year: int):
        years_subjects = YearsSubjectsTable.select_by_year(year)
        print(years_subjects)
        years_subjects = set([x.subject for x in years_subjects])
        print(years_subjects)
        subjects = SubjectsTable.select_all()
        text1 = text2 = text3 = '\n'
        for subject in subjects:
            checked = ''
            if subject.id in years_subjects:
                checked = ' checked'
            text = '<p><input type="checkbox" name="subject" value="' + str(subject.id) + '"' + checked + '>' + \
                   subject.name + '</p>\n'
            if subject.type == 'i':
                text1 += text
            elif subject.type == 'g':
                text2 += text
            else:
                text3 += text
        for file_name in glob.glob(Config.TEMPLATES_FOLDER + '/' + str(year) + '/**/*.html', recursive=True):
            data = SplitFile(file_name)
            data.insert_after_comment(' list of year_individual tours ', text1)
            data.insert_after_comment(' list of year_group tours ', text2)
            data.insert_after_comment(' list of year_another tours ', text3)
            data.save_file()
