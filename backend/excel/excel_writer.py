from backend.excel.excel_parent import ExcelParentWriter
from backend.queries.help import class_min, compare
from ..database import GroupResult, Result, Student, StudentCode, Subject, SubjectStudent, Team, TeamStudent


class ExcelSubjectWriter(ExcelParentWriter):
    def __init__(self, subject, year):
        self.subject = subject
        self.c = class_min(year)

    def __gen_sheet__(self, worksheet, data: list, cls: int):
        self.__head__(worksheet, 'Место', 'Фамилия', 'Имя', 'Класс', 'Балл', 'Балл в рейтинг',
                      title='{}, {} класс'.format(self.subject, cls), widths=[8, 20, 20, 10, 10, 10])
        self.__write__(worksheet, data, 2, cols_cnt=5)

    def write(self, filename: str, data: list):
        self.__styles__(filename)
        for x in data:
            if x:
                self.__gen_sheet__(self.workbook.add_worksheet('{} класс'.format(self.c)), x, self.c)
            self.c += 1
        self.workbook.close()


class ExcelClassesWriter(ExcelParentWriter):
    def __init__(self, year):
        self.c = class_min(year)

    def __gen_sheet__(self, worksheet, data: list, cls=None):
        self.__head__(worksheet, 'Место', 'Класс', 'Сумма', 'Не 0',
                      title=str(cls) + ' класс' if cls else 'Общий', widths=[10, 10, 10, 10])
        self.__write__(worksheet, data, 2, cols_cnt=3)
        sm1, sm2 = sum(x[2] for x in data), sum(x[3] for x in data)
        self.__footer__(worksheet, ['Итого: ', sm1, sm2], [2], [self.head_style], len(data) + 3)

    def write(self, filename: str, data: list, all: list):
        self.__styles__(filename)
        self.__gen_sheet__(self.workbook.add_worksheet('Общий'), all)
        for x in data:
            if x:
                self.__gen_sheet__(self.workbook.add_worksheet('{} класс'.format(self.c)), x, self.c)
            self.c += 1
        self.workbook.close()


class ExcelCodesWriter(ExcelParentWriter):
    def __init__(self, year):
        self.head_end = ['Код']
        # if year > 0 else ['Код 1', 'Код 2'] # НШ передумала :)

    def __gen_sheet__(self, worksheet, data: list):
        self.__head__(worksheet, 'Фамилия', 'Имя', 'Класс', *self.head_end)
        self.__write__(worksheet, data, cols_cnt=2 + len(self.head_end))

    def write(self, filename: str, data: list):
        self.__styles__(filename)
        self.__gen_sheet__(self.workbook.add_worksheet('Кодировка'), data)
        self.workbook.close()


class ExcelDiplomaWriter(ExcelParentWriter):
    def __init__(self, year):
        self.year = year

    def __gen_sheet__(self, worksheet, data: list):
        self.__head__(worksheet, 'Класс', 'ФИО', 'Место', widths=[30, 30, 15])
        new_data, sz = [], 3
        for x in data:
            student, position, subject = x
            x = ['учени{} {} класса'.format('ца' if student.gender else 'к', student.class_name()), student.name(),
                 'за {} место'.format(position), *subject.diploma.split('\n')]
            sz = max(sz, len(x))
            new_data.append(x)
        self.__write__(worksheet, new_data, border=sz)
        if sz == 4:
            worksheet.set_column(3, 3, 30)
            worksheet.write(0, 3, 'Предмет', self.center_style)
        elif sz > 4:
            worksheet.set_column(3, sz - 1, 30)
            worksheet.merge_range(0, 3, 0, sz - 1, 'Предмет', self.center_style)

    def write(self, filename: str, dip1: list, dip2: list, dip3: list):
        cmp = [lambda x: x[2].id, lambda x: x[0].class_n, lambda x: x[1], lambda x: x[0].class_l, lambda x: x[0].name()]
        dip1.sort(key=compare(*cmp, field=True))
        cmp[1], cmp[2] = cmp[2], cmp[1]
        dip2.sort(key=compare(*cmp, field=True))
        dip3.sort(key=compare(*cmp, field=True))
        self.__styles__(filename)
        self.__gen_sheet__(self.workbook.add_worksheet('Индивидуальные туры'), dip1)
        self.__gen_sheet__(self.workbook.add_worksheet('Групповые туры'), dip2)
        self.__gen_sheet__(self.workbook.add_worksheet('Командный тур'), dip3)
        self.workbook.close()


class ExcelFullWriter(ExcelParentWriter):
    def __init__(self, year: int):
        self.year = year
        self.head_begin = ['Код'] if year > 0 else ['Код 1', 'Код 2']

    def __gen_codes__(self, worksheet):
        self.__head__(worksheet, *self.head_begin, 'Фамилия', 'Имя', 'Класс', 'Пол', 'Команда')
        data = []
        for code in StudentCode.select_by_year(self.year):
            x = self.students[code.student]
            codes = [code.code1] if self.year > 0 else [code.code1, code.code2]
            data.append([*codes, x[0], x[1], x[2], x[3], '' if code.student not in self.student_team else
                        self.later_teams[self.student_team[code.student]]])
        self.__write__(worksheet, data, cols_cnt=3 + len(self.head_begin))

    def __gen_teams__(self, worksheet):
        self.__head__(worksheet, 'Вертикаль', 'Название')
        data = []
        for team in self.full_teams:
            data.append([team.later, team.name])
        self.__write__(worksheet, data, cols_cnt=1)

    def __gen_results__(self, worksheet):
        self.__head__(worksheet, 'Предмет', 'Код', 'Балл', 'Сумма', 'Чист. балл')
        data = []
        for r in Result.select_by_year(self.year):
            data.append([self.subjects[r.subject], r.user, r.text_result, r.result, r.net_score])
        self.__write__(worksheet, data, cols_cnt=4)

    def __gen_group_results__(self, worksheet):
        self.__head__(worksheet, 'Команда', 'Предмет', 'Результат')
        max_len, data = 0, []
        for team in self.teams:
            for result in GroupResult.select_by_team(team):
                students = []
                if result.subject in self.student_subject and team in self.student_subject[result.subject]:
                    students = [' '.join(self.students[_][:-1]) for _ in self.student_subject[result.subject][team]]
                    max_len = max(max_len, len(students))
                data.append([self.teams[team], self.subjects[result.subject], result.result, *students])
        self.__write__(worksheet, data)
        if max_len == 1:
            worksheet.set_column(3, 3, 45)
            worksheet.write(0, 3, 'Участники', self.center_style)
        elif max_len > 1:
            worksheet.set_column(3, max_len + 2, 45)
            worksheet.merge_range(0, 3, 0, max_len + 2, 'Участники', self.center_style)

    def write(self, filename: str):
        self.students = {_.id: [_.name_1, _.name_2, _.class_name(), _.get_gender()] for _ in Student.select_all(self.year)}
        self.subjects = {_.id: _.name for _ in Subject.select_all()}
        self.full_teams = Team.select_by_year(self.year)
        self.later_teams = {_.id: _.later for _ in self.full_teams}
        self.teams = {_.id: _.name for _ in self.full_teams}
        self.student_team = {y.student: y.team for x in self.teams for y in TeamStudent.select_by_team(x)}
        self.student_subject = {}
        for student in SubjectStudent.select_by_year(self.year):
            sub, stud, team = student.subject, student.student, self.student_team[student.student]
            if sub not in self.student_subject:
                self.student_subject[sub] = {}
            if team not in self.student_subject[sub]:
                self.student_subject[sub][team] = []
            self.student_subject[sub][team].append(stud)

        self.__styles__(filename)
        self.__gen_codes__(self.workbook.add_worksheet('Коды'))
        self.__gen_teams__(self.workbook.add_worksheet('Команды'))
        self.__gen_results__(self.workbook.add_worksheet('Результаты'))
        self.__gen_group_results__(self.workbook.add_worksheet('Групповые результаты'))
        self.workbook.close()
