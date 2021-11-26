import xlsxwriter


def add_row(worksheet, idx, *args):
    i = 0
    for arg in args:
        worksheet.write(idx, i, arg)
        i += 1


class ExcelSubjectWriter:
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
        self.__head__(worksheet, 'Место', 'Фамилия', 'Имя', 'Класс', 'Балл', 'Балл в рейтинг')
        row_idx = 1
        for row in data:
            add_row(worksheet, row_idx, *row)
            row_idx += 1
        worksheet.autofilter(0, 0, row_idx-1, 1)

    def write(self, filename: str, data: list):
        workbook = xlsxwriter.Workbook(filename)
        self.bold_style = workbook.add_format({'bold': True})
        c = 5
        for x in data:
            if x:
                self.__gen_sheet__(workbook.add_worksheet('{} класс'.format(c)), x)
            c += 1
        workbook.close()
