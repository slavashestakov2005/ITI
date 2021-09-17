import pandas as pd
from ..queries.file_creator import FileCreator, SplitFile
from ..queries.auto_generator import Generator
from ..queries.help import split_class
from ..database import SubjectsTable, YearSubject, YearsSubjectsTable, Team, TeamsTable, Student, StudentsTable,\
    StudentCode, StudentsCodesTable, Result, ResultsTable, TeamStudent, TeamsStudentsTable
from ..config import Config


def find(titles, exists, not_exists=None):
    i = 0
    for x in titles:
        t = x.lower()
        if exists in t and (not not_exists or not_exists not in t):
            return i
        i += 1
    return -1


class ExcelReader:
    RES = ['subject', 'code', 'result']
    CODES = ['name', 'cls', 'code', 'team']

    def __init__(self, file: str, year: int):
        self.file = file
        self.year = year

    def __frames__(self):
        sheet_name = self.sheet.sheet_names
        ans, codes = find(sheet_name, 'ответы'), find(sheet_name, 'код')
        self.result, self.code = list(self.sheet.parse([sheet_name[ans], sheet_name[codes]]).values())

    def __get_result_cols__(self):
        columns = self.result.columns
        sub, code = find(columns, 'предмет'), find(columns, 'номер')
        result = find(columns, 'балл', 'чист')
        frame = pd.DataFrame(self.result, columns=[columns[sub], columns[code], columns[result]])
        frame.columns = self.RES
        self.result = frame[frame[self.RES[0]].notna() & frame[self.RES[1]].notna() & frame[self.RES[2]].notna()]

    def __get_codes_cols__(self):
        columns = self.code.columns
        name, cls = columns[find(columns, 'имя')], columns[find(columns, 'класс')]
        code, team = columns[find(columns, 'код')], columns[find(columns, 'команда')]
        frame = pd.DataFrame(self.code, columns=[name, cls, code, team])
        frame.columns = self.CODES
        self.code = frame[frame[self.CODES[0]].notna() & frame[self.CODES[1]].notna() & frame[self.CODES[2]].notna()]

    def __gen_subject__(self):
        subjects = self.result[self.RES[0]].unique().tolist()
        all_subject = SubjectsTable.select_all()
        all_names = [_.name for _ in all_subject]
        all_map = {_.name: _.id for _ in all_subject}
        self.subjects = {}
        for subject in subjects:
            f = find(all_names, subject.lower())
            if f == -1:
                raise ValueError(subject)
            self.subjects[subject] = all_map[all_names[f]]

        for subject in self.subjects:
            ys = YearSubject([self.year, self.subjects[subject], 30, 30, 30, 30, 30, 0, 0, '', ''])
            YearsSubjectsTable.insert(ys)
        FileCreator.create_subjects(self.year, list(self.subjects.values()))
        Generator.gen_years_subjects_list(self.year)
        self.all_subjects = {_.id: _ for _ in all_subject}

    def __gen_teams__(self):
        teams = [str(_) for _ in self.code[self.CODES[3]].unique().tolist() if str(_) != 'nan']
        for team in teams:
            TeamsTable.insert(Team([None, 'Вертикаль ' + team, self.year, team]))
        self.teams = {}
        for team in teams:
            self.teams[team] = TeamsTable.select_by_year_and_later(self.year, team).id
        Generator.gen_teams(self.year)

    def __gen_students__(self):
        self.student = {}
        self.students_codes = []
        for i, row in self.code.iterrows():
            names = row[0].split()
            class_ = split_class(row[1])
            student = Student([None, names[0], names[1], class_[0], class_[1]])
            st = StudentsTable.select_by_student(student)
            if st.__is_none__:
                StudentsTable.insert(student)
                sid = StudentsTable.select_by_student(student).id
            else:
                student.id = sid = st.id
                StudentsTable.update(student)
            self.student[(row[0], row[1])] = sid
            c = StudentCode([self.year, int(row[2]), sid])
            StudentsCodesTable.insert(c)
            self.students_codes.append(int(row[2]))
            if str(row[3]) != 'nan':
                ts = TeamStudent([self.teams[str(row[3])], sid])
                TeamsStudentsTable.insert(ts)
        self.students_codes = set(self.students_codes)

    def __gen_results__(self):
        for i, row in self.result.iterrows():
            if row[0] in self.subjects and int(row[1]) in self.students_codes and str(row[2]) != 'nan':
                r = Result([self.year, self.subjects[row[0]], int(row[1]), row[2], 0, str(row[2])])
                ex = False
                try:
                    ResultsTable.insert(r)
                except Exception:
                    ex = True
                if ex:
                    ResultsTable.update(r)
        for subject in self.subjects.values():
            t = self.all_subjects[subject].type_str()
            Generator.gen_results(self.year, subject, str(self.year) + '/' + t + '/' + str(subject) + '.html')

    def __gen_pages__(self):
        Generator.gen_ratings(self.year)
        Generator.gen_timetable(self.year)
        data = SplitFile(Config.TEMPLATES_FOLDER + '/' + str(self.year) + '/subjects_for_year.html')
        data.insert_after_comment(' is_block ', '''
                    <p><input type="radio" name="is_block" value="0">Разблокировано</p>
                    <p><input type="radio" name="is_block" value="1" checked>Заблокировано</p>
                ''')
        data.save_file()

    def read(self):
        self.sheet = pd.ExcelFile(self.file)
        self.__frames__()
        self.__get_codes_cols__()
        self.__get_result_cols__()
        self.__gen_subject__()
        self.__gen_teams__()
        self.__gen_students__()
        self.__gen_results__()
        self.__gen_pages__()
