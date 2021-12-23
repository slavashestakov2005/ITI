from .log import Log
from .excel_parent import ExcelParentWriter
from ..database import StudentsCodesTable, UsersTable, HistoriesTable, ResultsTable, GroupResultsTable, AppealsTable, \
    SubjectsTable, TeamsTable, StudentsTable, TeamsStudentsTable, SubjectsStudentsTable


class ExcelSubjectWriter(ExcelParentWriter):
    def __init__(self, subject):
        self.subject = subject

    def __gen_sheet__(self, worksheet, data: list, cls: int):
        self.__head__(worksheet, 'Место', 'Фамилия', 'Имя', 'Класс', 'Балл', 'Балл в рейтинг',
                      title='{}, {} класс'.format(self.subject, cls), widths=[8, 20, 20, 10, 10, 10])
        self.__write__(worksheet, data, 2, cols_cnt=5)

    def write(self, filename: str, data: list):
        self.__styles__(filename)
        c = 5
        for x in data:
            if x:
                self.__gen_sheet__(self.workbook.add_worksheet('{} класс'.format(c)), x, c)
            c += 1
        self.workbook.close()


class ExcelClassesWriter(ExcelParentWriter):
    def __gen_sheet__(self, worksheet, data: list, cls=None):
        self.__head__(worksheet, 'Место', 'Класс', 'Сумма', 'Не 0',
                      title=str(cls) + ' класс' if cls else 'Общий', widths=[10, 10, 10, 10])
        self.__write__(worksheet, data, 2, cols_cnt=3)
        sm1, sm2 = sum(x[2] for x in data), sum(x[3] for x in data)
        self.__footer__(worksheet, ['Итого: ', sm1, sm2], [2], [self.head_style], len(data) + 3)

    def write(self, filename: str, data: list, all: list):
        self.__styles__(filename)
        self.__gen_sheet__(self.workbook.add_worksheet('Общий'), all)
        c = 5
        for x in data:
            if x:
                self.__gen_sheet__(self.workbook.add_worksheet('{} класс'.format(c)), x, c)
            c += 1
        self.workbook.close()


class ExcelCodesWriter(ExcelParentWriter):
    def __gen_sheet__(self, worksheet, data: list):
        self.__head__(worksheet, 'Фамилия', 'Имя', 'Класс', 'Код')
        self.__write__(worksheet, data, cols_cnt=3)

    def write(self, filename: str, data: list):
        self.__styles__(filename)
        self.__gen_sheet__(self.workbook.add_worksheet('Кодировка'), data)
        self.workbook.close()


class ExcelFullWriter(ExcelParentWriter):
    def __init__(self, year: int):
        self.year = year

    def __gen_codes__(self, worksheet):
        self.__head__(worksheet, 'Код', 'Фамилия', 'Имя', 'Класс', 'Команда')
        data = []
        for code in StudentsCodesTable.select_by_year(self.year):
            x = self.students[code.student]
            data.append([code.code, x[0], x[1], x[2], '' if code.student not in self.student_team else
                        self.later_teams[self.student_team[code.student]]])
        self.__write__(worksheet, data, cols_cnt=4)

    def __gen_teams__(self, worksheet):
        self.__head__(worksheet, 'Вертикаль', 'Название')
        data = []
        for team in self.full_teams:
            data.append([team.later, team.name])
        self.__write__(worksheet, data, cols_cnt=1)

    def __gen_history__(self, worksheet):
        self.__head__(worksheet, 'Время', 'Пользователь', 'Тип', 'Описание', 'Отмена', widths=[20, 15, 20, 25, 20])
        users = {_.id: _.login for _ in UsersTable.select_all()}
        data = []
        for his in HistoriesTable.select_all():
            if his.description[:1] == '@':
                sp = his.description.split('; ', 1)
                sp[0] = self.subjects[int(sp[0][1:])]
                his.description = '; '.join(sp)
            revert = '' if not his.revert else 'Отменено ' + users[int(his.revert)]
            data.append([his.time_str(), users[his.user], Log.actions[his.type], his.description, revert])
        self.__write__(worksheet, data, cols_cnt=4)

    def __gen_results__(self, worksheet):
        self.__head__(worksheet, 'Предмет', 'Код', 'Балл', 'Сумма', 'Чист. балл')
        data = []
        for r in ResultsTable.select_by_year(self.year):
            data.append([self.subjects[r.subject], r.user, r.text_result, r.result, r.net_score])
        self.__write__(worksheet, data, cols_cnt=4)

    def __gen_group_results(self, worksheet):
        self.__head__(worksheet, 'Команда', 'Предмет', 'Результат')
        max_len, data = 0, []
        for team in self.teams:
            for result in GroupResultsTable.select_by_team(team):
                students = []
                if result.subject in self.student_subject and team in self.student_subject[result.subject]:
                    students = [' '.join(self.students[_]) for _ in self.student_subject[result.subject][team]]
                    max_len = max(max_len, len(students))
                data.append([self.teams[team], self.subjects[result.subject], result.result, *students])
        self.__write__(worksheet, data, cols_cnt=2)
        if max_len == 1:
            worksheet.set_column(3, 3, 45)
            worksheet.write(0, 3, 'Участники', self.center_style)
        elif max_len > 1:
            worksheet.set_column(3, max_len + 2, 45)
            worksheet.merge_range(0, 3, 0, max_len + 2, 'Участники', self.center_style)

    def __gen_appeals__(self, worksheet):
        self.__head__(worksheet, 'Предмет', 'Код', 'Задания', 'Описание')
        data = []
        for appeal in AppealsTable.select_by_year(self.year):
            data.append([self.subjects[appeal.subject], appeal.student, appeal.tasks, appeal.description])
        self.__write__(worksheet, data, cols_cnt=3)

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

        self.__styles__(filename)
        self.__gen_codes__(self.workbook.add_worksheet('Коды'))
        self.__gen_teams__(self.workbook.add_worksheet('Команды'))
        self.__gen_history__(self.workbook.add_worksheet('История'))
        self.__gen_results__(self.workbook.add_worksheet('Результаты'))
        self.__gen_group_results(self.workbook.add_worksheet('Групповые результаты'))
        self.__gen_appeals__(self.workbook.add_worksheet('Апелляции'))
        self.workbook.close()
