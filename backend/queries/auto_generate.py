from .help import SplitFile, read_and_split_file, all_templates
from ..database import YearsTable, SubjectsTable


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
            data: SplitFile = read_and_split_file(file_name)
            data.insert_after_comment(' list of years (1) ', type1)
            data.insert_after_comment(' list of years (2) ', type2)
            data.insert_after_comment(' list of years (3) ', type3)
            print(file_name)
            if data.edited:
                with open(file_name, 'w', encoding='UTF-8') as f:
                    f.write(data.writable())

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
            data: SplitFile = read_and_split_file(file_name)
            data.insert_after_comment(' list of individual tours (1) ', type1)
            data.insert_after_comment(' list of group tours (1) ', type2)
            data.insert_after_comment(' list of another tours (1) ', type3)
            data.insert_after_comment(' list of individual tours (2) ', type4)
            data.insert_after_comment(' list of group tours (2) ', type5)
            data.insert_after_comment(' list of another tours (2) ', type6)
            print(file_name)
            if data.edited:
                with open(file_name, 'w', encoding='UTF-8') as f:
                    f.write(data.writable())

