from backend.excel.excel_parent import ExcelParentWriter
from backend.queries.help import compare


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

    def write(self, filename: str, diplomas: list, subjects: dict, students: dict):
        dip1, dip2, dip3 = [], [], []
        for diploma in diplomas:
            student_id, subject_id, place = diploma
            student, subject = students[student_id], subjects[subject_id]
            line, tp = [student, place, subject], subject.type
            if tp == 'i':
                dip1.append(line)
            elif tp == 'g':
                dip2.append(line)
            else:
                dip3.append(line)
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
