import xlsxwriter


def add_row(worksheet, idx, *args, style=None):
    i = 0
    for arg in args:
        if not style:
            worksheet.write(idx, i, arg)
        else:
            worksheet.write(idx, i, arg, style)
        i += 1


class ExcelSubjectWriter:
    def __init__(self, subject):
        self.subject = subject

    def __head__(self, worksheet, cls, *cols, widths=None):
        worksheet.freeze_panes(3, 0)
        idx = 0
        self.caps_text = self.subject + ', ' + str(cls) + ' класс'
        worksheet.merge_range('A1:F1', self.caps_text, self.caps_style)
        for col in cols:
            worksheet.write(2, idx, col, self.head_style)
            if widths:
                worksheet.set_column(idx, idx, widths[idx])
            idx += 1
        if not widths:
            worksheet.set_column(2  , idx-1, 15)

    def __gen_sheet__(self, worksheet, data: list, cls: int):
        self.__head__(worksheet, cls, 'Место', 'Фамилия', 'Имя', 'Класс', 'Балл', 'Балл в рейтинг', widths=[8, 20, 20, 10, 10, 10])
        row_idx = 3
        for row in data:
            add_row(worksheet, row_idx, *row, style=self.normal_style)
            row_idx += 1
        worksheet.autofilter(2, 0, row_idx-1, 5)

    def write(self, filename: str, data: list):
        workbook = xlsxwriter.Workbook(filename)
        self.head_style = workbook.add_format({'bold': True, 'border': 1, 'text_wrap': True})
        self.head_style.set_font_size(14)
        self.caps_style = workbook.add_format({'bold': True})
        self.caps_style.set_font_size(20)
        self.caps_style.set_align('center')
        self.normal_style = workbook.add_format({'border': 1})
        self.normal_style.set_font_size(14)
        c = 5
        for x in data:
            if x:
                self.__gen_sheet__(workbook.add_worksheet('{} класс'.format(c)), x, c)
            c += 1
        workbook.close()


class ExcelClassesWriter:
    def __head__(self, worksheet, cls, *cols, widths=None):
        worksheet.freeze_panes(3, 0)
        idx = 0
        self.caps_text = str(cls) + ' класс' if cls else 'Общий'
        worksheet.merge_range('A1:D1', self.caps_text, self.caps_style)
        for col in cols:
            worksheet.write(2, idx, col, self.head_style)
            if widths:
                worksheet.set_column(idx, idx, widths[idx])
            idx += 1
        if not widths:
            worksheet.set_column(2, idx-1, 15)

    def __gen_sheet__(self, worksheet, data: list, cls=None):
        self.__head__(worksheet, cls, 'Место', 'Класс', 'Сумма', 'Не 0', widths=[10, 10, 10, 10])
        row_idx, sm1, sm2 = 3, 0, 0
        for row in data:
            add_row(worksheet, row_idx, *row, style=self.normal_style)
            row_idx += 1
            sm1 += row[2]
            sm2 += row[3]
        worksheet.merge_range('A{0}:B{0}'.format(row_idx + 1), 'Итого: ', self.head_style)
        worksheet.write(row_idx, 2, sm1, self.normal_style)
        worksheet.write(row_idx, 3, sm2, self.normal_style)
        worksheet.autofilter(2, 0, row_idx, 3)

    def write(self, filename: str, data: list, all: list):
        workbook = xlsxwriter.Workbook(filename)
        self.head_style = workbook.add_format({'bold': True, 'border': 1, 'text_wrap': True})
        self.head_style.set_font_size(14)
        self.caps_style = workbook.add_format({'bold': True})
        self.caps_style.set_font_size(20)
        self.caps_style.set_align('center')
        self.normal_style = workbook.add_format({'border': 1})
        self.normal_style.set_font_size(14)
        self.__gen_sheet__(workbook.add_worksheet('Общий'), all)
        c = 5
        for x in data:
            if x:
                self.__gen_sheet__(workbook.add_worksheet('{} класс'.format(c)), x, c)
            c += 1
        workbook.close()


class ExcelCodesWriter:
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

    def __gen_sheet__(self, worksheet, data: list):
        self.__head__(worksheet, 'Фамилия', 'Имя', 'Класс', 'Код')
        row_idx = 1
        for row in data:
            add_row(worksheet, row_idx, *row)
            row_idx += 1
        worksheet.autofilter(0, 0, row_idx-1, 3)

    def write(self, filename: str, data: list):
        workbook = xlsxwriter.Workbook(filename)
        self.bold_style = workbook.add_format({'bold': True})
        self.__gen_sheet__(workbook.add_worksheet('Кодировка'), data)
        workbook.close()
