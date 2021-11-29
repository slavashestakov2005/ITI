import pandas as pd
from ..queries.file_creator import FileCreator, SplitFile
from ..queries.auto_generator import Generator
from ..queries.help import split_class
from ..database import SubjectsTable, YearSubject, YearsSubjectsTable, Team, TeamsTable, Student, StudentsTable, \
    StudentCode, StudentsCodesTable, Result, ResultsTable, TeamStudent, TeamsStudentsTable, HistoriesTable, UsersTable, \
    GroupResultsTable, AppealsTable, SubjectsStudentsTable
from ..config import Config
from .log import Log
import xlsxwriter


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
    STUDENTS = ['name', 'cls']

    def __init__(self, file: str, year: int, qtype: int):
        self.file = file
        self.year = year
        self.qtype = qtype

    def __frames__(self):
        sheet_name = list(self.sheet.keys())
        self.sheet = list(self.sheet.values())
        ans, codes = find(sheet_name, 'ответы'), find(sheet_name, 'код')
        self.result, self.code = self.sheet[ans], self.sheet[codes]

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

    def __get_students_cols__(self):
        columns = self.code.columns
        name, cls = columns[find(columns, 'имя')], columns[find(columns, 'класс')]
        frame = pd.DataFrame(self.code, columns=[name, cls])
        frame.columns = self.STUDENTS
        self.student = frame[frame[self.STUDENTS[0]].notna() & frame[self.STUDENTS[1]].notna()]

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
            ys = YearSubject([self.year, self.subjects[subject], 30, 30, 30, 30, 30, 0, 0, '', '', 0])
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
        result = []
        for i, row in self.result.iterrows():
            if row[0] in self.subjects and int(row[1]) in self.students_codes and str(row[2]) != 'nan':
                result.append(Result([self.year, self.subjects[row[0]], int(row[1]), row[2], 0, str(row[2]), 0]))
        ResultsTable.replace(result)
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

    def __gen_only_students__(self):
        for i, row in self.student.iterrows():
            names = row[0].split()
            class_ = split_class(row[1])
            student = Student([None, names[0], names[1], class_[0], class_[1]])
            st = StudentsTable.select_by_student(student)
            if st.__is_none__:
                StudentsTable.insert(student)
            else:
                StudentsTable.update(student)

    def read(self):
        self.sheet = pd.read_excel(self.file, sheet_name=None, engine="openpyxl")
        self.__frames__()
        if self.qtype == 2:
            self.__get_students_cols__()
            self.__gen_only_students__()
        else:
            self.__get_codes_cols__()
            self.__get_result_cols__()
            self.__gen_subject__()
            self.__gen_teams__()
            self.__gen_students__()
            self.__gen_results__()
            self.__gen_pages__()


def add_row(worksheet, idx, *args):
    i = 0
    for arg in args:
        worksheet.write(idx, i, arg)
        i += 1


class ExcelWriter:
    def __init__(self, year: int):
        self.year = year

    def __head__(self, worksheet, *cols, widths=None):
        worksheet.freeze_panes(1, 0)
        idx = 0
        for col in cols:
            worksheet.write(0, idx, col, self.bold_style)
            if widths:
                worksheet.set_column(idx, idx, widths[idx])
            idx += 1
        if not widths:
            worksheet.set_column(0, idx-1, 15)

    def __gen_codes__(self, worksheet):
        self.__head__(worksheet, 'Код', 'Фамилия', 'Имя', 'Класс', 'Команда')
        row_idx = 1
        for code in StudentsCodesTable.select_by_year(self.year):
            x = self.students[code.student]
            add_row(worksheet, row_idx, code.code, x[0], x[1], x[2],
                    '' if code.student not in self.student_team else self.later_teams[self.student_team[code.student]])
            row_idx += 1
        worksheet.autofilter(0, 0, row_idx-1, 4)

    def __gen_teams__(self, worksheet):
        self.__head__(worksheet, 'Вертикаль', 'Название')
        row_idx = 1
        for team in self.full_teams:
            add_row(worksheet, row_idx, team.later, team.name)
            row_idx += 1
        worksheet.autofilter(0, 0, row_idx-1, 1)

    def __gen_history__(self, worksheet):
        self.__head__(worksheet, 'Время', 'Пользователь', 'Тип', 'Описание', 'Отмена', widths=[20, 15, 20, 25, 20])
        users = {_.id: _.login for _ in UsersTable.select_all()}
        row_idx = 1
        for history in HistoriesTable.select_all():
            if history.description[:1] == '@':
                sp = history.description.split('; ', 1)
                sp[0] = self.subjects[int(sp[0][1:])]
                history.description = '; '.join(sp)
            revert = '' if not history.revert else 'Отменено ' + users[int(history.revert)]
            add_row(worksheet, row_idx, history.time_str(), users[history.user], Log.actions[history.type],
                    history.description, revert)
            row_idx += 1
        worksheet.autofilter(0, 0, row_idx-1, 4)

    def __gen_results__(self, worksheet):
        self.__head__(worksheet, 'Предмет', 'Код', 'Балл', 'Сумма', 'Чист. балл')
        row_idx = 1
        for result in ResultsTable.select_by_year(self.year):
            add_row(worksheet, row_idx, self.subjects[result.subject], result.user, result.text_result, result.result,
                    result.net_score)
            row_idx += 1
        worksheet.autofilter(0, 0, row_idx-1, 4)

    def __gen_group_results(self, worksheet):
        self.__head__(worksheet, 'Команда', 'Предмет', 'Результат')
        row_idx = 1
        max_len = 0
        for team in self.teams:
            for result in GroupResultsTable.select_by_team(team):
                students = []
                if result.subject in self.student_subject and team in self.student_subject[result.subject]:
                    students = [' '.join(self.students[_]) for _ in self.student_subject[result.subject][team]]
                    max_len = max(max_len, len(students))
                add_row(worksheet, row_idx, self.teams[team], self.subjects[result.subject], result.result, *students)
        worksheet.autofilter(0, 0, row_idx-1, 2)
        if max_len == 1:
            worksheet.set_column(3, 3, 35)
            worksheet.write(0, 3, 'Участники', self.center_style)
        elif max_len > 1:
            worksheet.set_column(3, max_len+2, 45)
            worksheet.merge_range(0, 3, 0, max_len+2, 'Участники', self.center_style)

    def __gen_appeals__(self, worksheet):
        self.__head__(worksheet, 'Предмет', 'Код', 'Задания', 'Описание')
        row_idx = 1
        for appeal in AppealsTable.select_by_year(self.year):
            add_row(worksheet, row_idx, self.subjects[appeal.subject], appeal.student, appeal.tasks, appeal.description)
        worksheet.autofilter(0, 0, row_idx-1, 3)

    def write(self, filename: str):
        self.students = {_.id: [_.name_1, _.name_2, _.class_name()] for _ in StudentsTable.select_all()}
        self.subjects = {_.id: _.name for _ in SubjectsTable.select_all()}
        self.full_teams = TeamsTable.select_all()
        self.later_teams = {_.id: _.later for _ in self.full_teams}
        self.teams = {_.id: _.name for _ in self.full_teams}
        self.student_team = {y.student: y.team for x in self.teams for y in TeamsStudentsTable.select_by_team(x)}
        self.student_subject = {}
        for student in SubjectsStudentsTable.select_by_year(self.year):
            sub, stud, team = student.subject, student.student, self.student_team[student.student]
            if sub not in self.student_subject:
                self.student_subject[sub] = {}
            if team not in self.student_subject[sub]:
                self.student_subject[sub][team] = []
            self.student_subject[sub][team].append(stud)

        workbook = xlsxwriter.Workbook(filename)
        self.bold_style = workbook.add_format({'bold': True})
        self.center_style = workbook.add_format({'bold': True, 'align': 'center'})
        self.__gen_codes__(workbook.add_worksheet('Коды'))
        self.__gen_teams__(workbook.add_worksheet('Команды'))
        self.__gen_history__(workbook.add_worksheet('История'))
        self.__gen_results__(workbook.add_worksheet('Результаты'))
        self.__gen_group_results(workbook.add_worksheet('Групповые результаты'))
        self.__gen_appeals__(workbook.add_worksheet('Апелляции'))
        workbook.close()
