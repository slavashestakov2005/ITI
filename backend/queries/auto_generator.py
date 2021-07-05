from .help import SplitFile, all_templates
from ..database import YearsTable, SubjectsTable, YearsSubjectsTable, StudentsTable
from backend.config import Config
import glob
'''
    class Generator             Заменяет комментарии специального вида на код.
        gen_years_lists()                   Изменяет списки годов.
        gen_subjects_lists()                Изменяет глобальные списки предметов.
        gen_years_subjects_list(year)       Изменяет списки предметов для одного года.
        gen_students_list(class_n)          Изменяет таблицу учеников класса class_n.
        gen_codes(year)                     Генерирует страницу с кодами участников.
'''


class Generator:
    @staticmethod
    def gen_years_lists():
        years = YearsTable.select_all()
        type1 = type2 = type3 = type4 = '\n'
        for year in years:
            type1 += '<a href="' + str(year.year) + '/main.html">ИТИ-' + str(year.year) + "</a>\n"
            type2 += '<a href="../' + str(year.year) + '/main.html">ИТИ-' + str(year.year) + "</a>\n"
            type3 += '<a href="../../' + str(year.year) + '/main.html">ИТИ-' + str(year.year) + "</a>\n"
            type4 += '<a href="../../../' + str(year.year) + '/main.html">ИТИ-' + str(year.year) + "</a>\n"
        for file_name in all_templates():
            data = SplitFile(file_name)
            data.insert_after_comment(' list of years (1) ', type1)
            data.insert_after_comment(' list of years (2) ', type2)
            data.insert_after_comment(' list of years (3) ', type3)
            data.insert_after_comment(' list of years (4) ', type4)
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
        years_subjects = set([x.subject for x in years_subjects])
        subjects = SubjectsTable.select_all()
        text1 = text2 = text3 = text4 = text5 = '\n'
        for subject in subjects:
            checked = ''
            if subject.id in years_subjects:
                checked = ' checked'
                if subject.type == 'i':
                    text4 += '<p><a href="individual/' + str(subject.id) + '.html">' + subject.name + '</a></p>\n'
                elif subject.type == 'g':
                    text5 += '<p><a href="group/' + str(subject.id) + '.html">' + subject.name + '</a></p>\n'
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
            data.insert_after_comment(' list of year_individual tour (main page) ', text4)
            data.insert_after_comment(' list of year_group tour (main page) ', text5)
            data.save_file()

    @staticmethod
    def gen_students_list(class_n: int):
        file_name = Config.TEMPLATES_FOLDER + '/students_' + str(class_n) + '.html'
        students = StudentsTable.select_by_class_n(class_n)
        length = len(students)
        m1 = length // 3
        m2 = length * 2 // 3
        text1 = text2 = text3 = '\n'
        for i in range(0, m1):
            text1 += '<tr><td>' + students[i].name_1 + '</td><td>' + students[i].name_2 + '</td><td>' +\
                     str(students[i].class_n) + students[i].class_l + '</td></tr>\n'
        for i in range(m1, m2):
            text2 += '<tr><td>' + students[i].name_1 + '</td><td>' + students[i].name_2 + '</td><td>' + \
                     str(students[i].class_n) + students[i].class_l + '</td></tr>\n'
        for i in range(m2, length):
            text3 += '<tr><td>' + students[i].name_1 + '</td><td>' + students[i].name_2 + '</td><td>' + \
                     str(students[i].class_n) + students[i].class_l + '</td></tr>\n'
        data = SplitFile(file_name)
        data.insert_after_comment(' students_table 1 ', text3)
        data.insert_after_comment(' students_table 2 ', text2)
        data.insert_after_comment(' students_table 3 ', text1)
        data.save_file()

    @staticmethod
    def gen_codes(year: int):
        file_name = Config.TEMPLATES_FOLDER + "/" + str(year) + "/codes.html"
        students = StudentsTable.select_all()
        # sort list
        length = len(students)
        m1 = length // 3
        m2 = length * 2 // 3
        text1 = text2 = text3 = '\n'
        for i in range(0, m1):
            text1 += '<tr><td>' + str(students[i].class_n) + students[i].class_l + '</td><td>' + students[i].name_1 + \
                     '</td><td>' + students[i].name_2 + '</td><td>' + str(students[i].code) + '</td></tr>'
        for i in range(m1, m2):
            text2 += '<tr><td>' + str(students[i].class_n) + students[i].class_l + '</td><td>' + students[i].name_1 + \
                     '</td><td>' + students[i].name_2 + '</td><td>' + str(students[i].code) + '</td></tr>'
        for i in range(m2, length):
            text3 += '<tr><td>' + str(students[i].class_n) + students[i].class_l + '</td><td>' + students[i].name_1 + \
                     '</td><td>' + students[i].name_2 + '</td><td>' + str(students[i].code) + '</td></tr>'
        data = SplitFile(file_name)
        data.insert_after_comment(' codes_table 1 ', text3)
        data.insert_after_comment(' codes_table 2 ', text2)
        data.insert_after_comment(' codes_table 3 ', text1)
        data.save_file()
