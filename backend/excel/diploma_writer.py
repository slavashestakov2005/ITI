import logging
from .__parent_writer__ import ExcelParentWriter


class ExcelDiplomaWriter(ExcelParentWriter):
    def __gen_sheet__(self, worksheet, data: list):
        self.__head__(worksheet, 'Класс', 'ФИО', 'Место', widths=[30, 30, 15])
        new_data, sz = [], 3
        for x in data:
            student, position, subject = x
            x = ['учени{} {} класса'.format('ца' if student['gender'] == '1' else 'к', student['class']), student['name_all'],
                 'за {} место'.format(position), *subject['diploma'].split(r'\n')]
            sz = max(sz, len(x))
            new_data.append(x)
        self.__write__(worksheet, new_data, border=sz)
        if sz == 4:
            worksheet.set_column(3, 3, 30)
            worksheet.write(0, 3, 'Предмет', self.center_style)
        elif sz > 4:
            worksheet.set_column(3, sz - 1, 30)
            worksheet.merge_range(0, 3, 0, sz - 1, 'Предмет', self.center_style)
    
    @staticmethod
    def order_ind_diploma(x):
        return x[2]['id'], x[0]['class_n'], x[1], x[0]['class_latter'], x[0]['name_all']

    @staticmethod
    def order_gr_diploma(x):
        return x[2]['id'], x[1], x[0]['class_n'], x[0]['class_latter'], x[0]['name_all']

    def write(self, filename: str, diplomas: list, subjects: dict, students: dict):
        missing_students = set()
        missing_subjects = set()
        dip1, dip2, dip3 = [], [], []
        for diploma in diplomas:
            student_id, subject_id, place = diploma
            student = students.get(student_id)
            subject = subjects.get(subject_id)
            if student is None:
                missing_students.add(student_id)
                continue
            if subject is None:
                missing_subjects.add(subject_id)
                continue
            line, tp = [student, place, subject], subject['type']
            if tp == 'i':
                dip1.append(line)
            elif tp == 'g':
                dip2.append(line)
            else:
                dip3.append(line)
        if missing_students or missing_subjects:
            logging.warning(
                "Diploma writer skipped missing entries: students=%s subjects=%s",
                sorted(missing_students),
                sorted(missing_subjects),
            )
        dip1.sort(key=ExcelDiplomaWriter.order_ind_diploma)
        dip2.sort(key=ExcelDiplomaWriter.order_gr_diploma)
        dip3.sort(key=ExcelDiplomaWriter.order_gr_diploma)
        self.__styles__(filename)
        self.__gen_sheet__(self.workbook.add_worksheet('Индивидуальные туры'), dip1)
        self.__gen_sheet__(self.workbook.add_worksheet('Групповые туры'), dip2)
        self.__gen_sheet__(self.workbook.add_worksheet('Командный тур'), dip3)
        self.workbook.close()
